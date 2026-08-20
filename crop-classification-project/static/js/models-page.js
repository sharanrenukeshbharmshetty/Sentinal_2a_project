/**
 * =============================================================================
 * CropVision AI — Models Page JavaScript
 * 
 * Loads metrics.json and dynamically creates charts, confusion matrices,
 * and comparison tables. Works with Live Server — no Flask needed.
 * =============================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
    loadMetrics();
});

async function loadMetrics() {
    const loadingEl = document.getElementById('metricsLoading');
    const contentEl = document.getElementById('metricsContent');
    const errorEl = document.getElementById('metricsError');

    try {
        const response = await fetch('models/metrics.json');
        if (!response.ok) throw new Error('Metrics file not found');
        
        const metrics = await response.json();
        
        // Hide loading, show content
        if (loadingEl) loadingEl.style.display = 'none';
        if (contentEl) contentEl.style.display = 'block';

        // Populate metric cards
        populateMetricCards(metrics);
        
        // Build charts
        buildAccuracyChart(metrics);
        buildRadarChart(metrics);
        
        // Build confusion matrices
        buildConfusionMatrix('rf', metrics.random_forest.confusion_matrix, metrics.crop_classes);
        buildConfusionMatrix('ada', metrics.adaboost.confusion_matrix, metrics.crop_classes);
        
        // Build comparison table
        buildMetricsTable(metrics);

    } catch (err) {
        console.error('Failed to load metrics:', err);
        if (loadingEl) loadingEl.style.display = 'none';
        if (errorEl) errorEl.style.display = 'block';
    }
}

function pct(val) {
    return (val * 100).toFixed(2) + '%';
}

function populateMetricCards(metrics) {
    const rf = metrics.random_forest;
    const ada = metrics.adaboost;

    document.getElementById('rfAccuracy').textContent = pct(rf.accuracy);
    document.getElementById('rfPrecision').textContent = pct(rf.precision);
    document.getElementById('rfRecall').textContent = pct(rf.recall);
    document.getElementById('rfF1').textContent = pct(rf.f1_score);

    document.getElementById('adaAccuracy').textContent = pct(ada.accuracy);
    document.getElementById('adaPrecision').textContent = pct(ada.precision);
    document.getElementById('adaRecall').textContent = pct(ada.recall);
    document.getElementById('adaF1').textContent = pct(ada.f1_score);
}

function buildAccuracyChart(metrics) {
    const ctx = document.getElementById('accuracyChart');
    if (!ctx) return;

    const chartFont = { family: 'Inter', weight: '500' };
    const rfColor = 'rgba(31, 111, 61, 0.85)';
    const rfBorder = 'rgba(31, 111, 61, 1)';
    const adaColor = 'rgba(52, 152, 219, 0.85)';
    const adaBorder = 'rgba(52, 152, 219, 1)';

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Accuracy', 'Precision', 'Recall', 'F1-Score'],
            datasets: [
                {
                    label: 'Random Forest',
                    data: [
                        (metrics.random_forest.accuracy * 100).toFixed(2),
                        (metrics.random_forest.precision * 100).toFixed(2),
                        (metrics.random_forest.recall * 100).toFixed(2),
                        (metrics.random_forest.f1_score * 100).toFixed(2)
                    ],
                    backgroundColor: rfColor,
                    borderColor: rfBorder,
                    borderWidth: 1,
                    borderRadius: 8
                },
                {
                    label: 'AdaBoost',
                    data: [
                        (metrics.adaboost.accuracy * 100).toFixed(2),
                        (metrics.adaboost.precision * 100).toFixed(2),
                        (metrics.adaboost.recall * 100).toFixed(2),
                        (metrics.adaboost.f1_score * 100).toFixed(2)
                    ],
                    backgroundColor: adaColor,
                    borderColor: adaBorder,
                    borderWidth: 1,
                    borderRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { font: { ...chartFont, size: 13 }, usePointStyle: true, padding: 20 }
                },
                tooltip: {
                    callbacks: { label: ctx => `${ctx.dataset.label}: ${parseFloat(ctx.parsed.y).toFixed(2)}%` }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: { display: true, text: 'Score (%)', font: chartFont },
                    grid: { color: 'rgba(0,0,0,0.06)' }
                },
                x: {
                    grid: { display: false },
                    ticks: { font: chartFont }
                }
            }
        }
    });
}

function buildRadarChart(metrics) {
    const ctx = document.getElementById('radarChart');
    if (!ctx) return;

    const chartFont = { family: 'Inter', weight: '500' };
    const rfBorder = 'rgba(31, 111, 61, 1)';
    const adaBorder = 'rgba(52, 152, 219, 1)';

    new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Accuracy', 'Precision', 'Recall', 'F1-Score'],
            datasets: [
                {
                    label: 'Random Forest',
                    data: [
                        (metrics.random_forest.accuracy * 100).toFixed(2),
                        (metrics.random_forest.precision * 100).toFixed(2),
                        (metrics.random_forest.recall * 100).toFixed(2),
                        (metrics.random_forest.f1_score * 100).toFixed(2)
                    ],
                    backgroundColor: 'rgba(31, 111, 61, 0.15)',
                    borderColor: rfBorder,
                    borderWidth: 2,
                    pointBackgroundColor: rfBorder,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5
                },
                {
                    label: 'AdaBoost',
                    data: [
                        (metrics.adaboost.accuracy * 100).toFixed(2),
                        (metrics.adaboost.precision * 100).toFixed(2),
                        (metrics.adaboost.recall * 100).toFixed(2),
                        (metrics.adaboost.f1_score * 100).toFixed(2)
                    ],
                    backgroundColor: 'rgba(52, 152, 219, 0.15)',
                    borderColor: adaBorder,
                    borderWidth: 2,
                    pointBackgroundColor: adaBorder,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { font: { ...chartFont, size: 13 }, usePointStyle: true, padding: 20 }
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { stepSize: 20, backdropColor: 'transparent', font: { size: 11 } },
                    grid: { color: 'rgba(0,0,0,0.08)' },
                    pointLabels: { font: { ...chartFont, size: 13 } }
                }
            }
        }
    });
}

function buildConfusionMatrix(prefix, matrix, classes) {
    const headerRow = document.getElementById(`${prefix}CmHeader`);
    const tbody = document.getElementById(`${prefix}CmBody`);
    if (!headerRow || !tbody) return;

    // Build header
    headerRow.innerHTML = '<th></th>' + classes.map(c => `<th>${c}</th>`).join('');

    // Build rows
    tbody.innerHTML = '';
    matrix.forEach((row, i) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<th>${classes[i]}</th>`;
        row.forEach((val, j) => {
            const td = document.createElement('td');
            td.textContent = val;
            td.dataset.value = val;

            if (i === j) {
                // Diagonal — correct predictions
                const intensity = Math.min(val / 120, 1);
                td.style.backgroundColor = `rgba(31, 111, 61, ${0.15 + intensity * 0.55})`;
                td.style.color = intensity > 0.4 ? '#fff' : '#1f6f3d';
                td.style.fontWeight = '700';
            } else {
                // Off-diagonal — errors
                const intensity = Math.min(val / 50, 1);
                td.style.backgroundColor = `rgba(220, 53, 69, ${intensity * 0.35})`;
                if (val > 0) td.style.color = '#8b1a2b';
            }

            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}

function buildMetricsTable(metrics) {
    const tbody = document.getElementById('metricsTableBody');
    if (!tbody) return;

    const metricPairs = [
        ['Accuracy', metrics.random_forest.accuracy, metrics.adaboost.accuracy],
        ['Precision', metrics.random_forest.precision, metrics.adaboost.precision],
        ['Recall', metrics.random_forest.recall, metrics.adaboost.recall],
        ['F1-Score', metrics.random_forest.f1_score, metrics.adaboost.f1_score]
    ];

    tbody.innerHTML = '';
    metricPairs.forEach(([name, rfVal, adaVal]) => {
        const diff = ((rfVal - adaVal) * 100).toFixed(2);
        const diffClass = rfVal > adaVal ? 'positive' : 'negative';
        const diffPrefix = rfVal > adaVal ? '+' : '';

        tbody.innerHTML += `
            <tr>
                <td><strong>${name}</strong></td>
                <td>${(rfVal * 100).toFixed(2)}%</td>
                <td>${(adaVal * 100).toFixed(2)}%</td>
                <td class="${diffClass}">${diffPrefix}${diff}%</td>
            </tr>
        `;
    });
}
