/**
 * K6 Load Testing Script for Fast Embedding API
 * 
 * Run with:
 *   k6 run benchmarks/k6-load-test.js
 * 
 * Or with custom options:
 *   k6 run --vus 10 --duration 30s benchmarks/k6-load-test.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const embedDuration = new Trend('embed_duration');
const batchEmbedDuration = new Trend('batch_embed_duration');
const requestCounter = new Counter('total_requests');

// Configuration
const BASE_URL = __ENV.API_URL || 'http://localhost:8000';
const MODEL_NAME = 'BAAI/bge-small-en-v1.5';

// Test configuration
export const options = {
    stages: [
        { duration: '30s', target: 10 },  // Ramp up to 10 users
        { duration: '1m', target: 10 },   // Stay at 10 users
        { duration: '30s', target: 20 },  // Ramp up to 20 users
        { duration: '1m', target: 20 },   // Stay at 20 users
        { duration: '30s', target: 0 },   // Ramp down to 0
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'], // 95% of requests should be below 500ms
        errors: ['rate<0.1'],              // Error rate should be below 10%
        http_req_failed: ['rate<0.01'],   // Failed requests should be below 1%
    },
};

// Sample texts for testing
const sampleTexts = [
    'The quick brown fox jumps over the lazy dog',
    'Machine learning is transforming the world of technology',
    'Python is an excellent programming language for data science',
    'Embeddings capture the semantic meaning of text',
    'Natural language processing enables computers to understand human language',
    'Deep learning models have revolutionized artificial intelligence',
    'Vector databases are essential for similarity search',
    'Transformers are the foundation of modern NLP models',
    'Semantic search provides more relevant results than keyword matching',
    'Large language models can generate human-like text',
];

function getRandomText() {
    return sampleTexts[Math.floor(Math.random() * sampleTexts.length)];
}

function getRandomTexts(count) {
    const texts = [];
    for (let i = 0; i < count; i++) {
        texts.push(getRandomText());
    }
    return texts;
}

export function setup() {
    // Test API availability
    const healthRes = http.get(`${BASE_URL}/health`);
    if (healthRes.status !== 200) {
        throw new Error('API is not available. Please start the server first.');
    }
    console.log('API is ready. Starting load test...');
}

export default function () {
    requestCounter.add(1);

    // Randomly choose between single and batch requests (70% single, 30% batch)
    const useBatch = Math.random() > 0.7;

    if (useBatch) {
        // Batch embedding request
        const batchSize = Math.floor(Math.random() * 5) + 3; // 3-7 texts
        const payload = JSON.stringify({
            model_name: MODEL_NAME,
            texts: getRandomTexts(batchSize),
        });

        const params = {
            headers: { 'Content-Type': 'application/json' },
            tags: { request_type: 'batch' },
        };

        const res = http.post(`${BASE_URL}/embed/batch`, payload, params);

        const success = check(res, {
            'batch status is 200': (r) => r.status === 200,
            'batch has embeddings': (r) => {
                try {
                    const body = JSON.parse(r.body);
                    return body.embeddings && body.embeddings.length === batchSize;
                } catch (e) {
                    return false;
                }
            },
            'batch response time OK': (r) => r.timings.duration < 1000,
        });

        if (success) {
            batchEmbedDuration.add(res.timings.duration);
        } else {
            errorRate.add(1);
        }
    } else {
        // Single embedding request
        const payload = JSON.stringify({
            model_name: MODEL_NAME,
            text: getRandomText(),
        });

        const params = {
            headers: { 'Content-Type': 'application/json' },
            tags: { request_type: 'single' },
        };

        const res = http.post(`${BASE_URL}/embed`, payload, params);

        const success = check(res, {
            'single status is 200': (r) => r.status === 200,
            'single has embedding': (r) => {
                try {
                    const body = JSON.parse(r.body);
                    return body.embedding && body.embedding.length > 0;
                } catch (e) {
                    return false;
                }
            },
            'single response time OK': (r) => r.timings.duration < 500,
        });

        if (success) {
            embedDuration.add(res.timings.duration);
        } else {
            errorRate.add(1);
        }
    }

    // Small delay between requests
    sleep(0.1);
}

export function handleSummary(data) {
    return {
        'benchmarks/k6-results.json': JSON.stringify(data, null, 2),
        stdout: textSummary(data, { indent: ' ', enableColors: true }),
    };
}

function textSummary(data, options) {
    const indent = options.indent || '';
    const enableColors = options.enableColors !== false;

    let summary = '\n';
    summary += `${indent}📊 K6 Load Test Results\n`;
    summary += `${indent}${'='.repeat(60)}\n\n`;

    // Scenarios
    summary += `${indent}🔄 Test Duration: ${data.state.testRunDurationMs / 1000}s\n`;
    summary += `${indent}👥 Virtual Users: Peak ${options.stages ? options.stages[3].target : 'N/A'}\n\n`;

    // HTTP metrics
    const httpReqDuration = data.metrics.http_req_duration;
    if (httpReqDuration) {
        summary += `${indent}⏱️  Response Times:\n`;
        summary += `${indent}   Min:    ${httpReqDuration.values.min.toFixed(2)}ms\n`;
        summary += `${indent}   Avg:    ${httpReqDuration.values.avg.toFixed(2)}ms\n`;
        summary += `${indent}   Median: ${httpReqDuration.values.med.toFixed(2)}ms\n`;
        summary += `${indent}   P95:    ${httpReqDuration.values['p(95)'].toFixed(2)}ms\n`;
        summary += `${indent}   P99:    ${httpReqDuration.values['p(99)'].toFixed(2)}ms\n`;
        summary += `${indent}   Max:    ${httpReqDuration.values.max.toFixed(2)}ms\n\n`;
    }

    // Throughput
    const httpReqs = data.metrics.http_reqs;
    if (httpReqs) {
        const duration = data.state.testRunDurationMs / 1000;
        const rps = httpReqs.values.count / duration;
        summary += `${indent}🚀 Throughput:\n`;
        summary += `${indent}   Total Requests: ${httpReqs.values.count}\n`;
        summary += `${indent}   Requests/sec:   ${rps.toFixed(2)}\n\n`;
    }

    // Error rate
    const errors = data.metrics.errors;
    if (errors) {
        const errorPercent = (errors.values.rate * 100).toFixed(2);
        summary += `${indent}❌ Error Rate: ${errorPercent}%\n\n`;
    }

    // Custom metrics
    if (data.metrics.embed_duration) {
        summary += `${indent}📝 Single Embed Metrics:\n`;
        summary += `${indent}   Avg: ${data.metrics.embed_duration.values.avg.toFixed(2)}ms\n\n`;
    }

    if (data.metrics.batch_embed_duration) {
        summary += `${indent}📦 Batch Embed Metrics:\n`;
        summary += `${indent}   Avg: ${data.metrics.batch_embed_duration.values.avg.toFixed(2)}ms\n\n`;
    }

    summary += `${indent}${'='.repeat(60)}\n`;

    return summary;
}
