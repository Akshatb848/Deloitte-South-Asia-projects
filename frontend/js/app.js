/**
 * Education Intelligence Dashboard
 * Ministry of Education, Government of India
 * Technology Partner: Deloitte Touche Tohmatsu
 */

// =============================================================================
// Application State
// =============================================================================

const AppState = {
    currentMonth: 'April_2025',
    newsletterData: null,
    charts: {},
    apiBaseUrl: 'http://localhost:8000/api'
};

// =============================================================================
// Data Loading
// =============================================================================

async function loadNewsletterData() {
    try {
        const response = await fetch('../data/newsletter_data.json');
        AppState.newsletterData = await response.json();
        console.log('Newsletter data loaded successfully');
        return AppState.newsletterData;
    } catch (error) {
        console.error('Error loading newsletter data:', error);
        // Fallback: Use embedded data
        return null;
    }
}

// =============================================================================
// Calendar Timeline
// =============================================================================

function initializeTimeline() {
    const timelineMonths = document.getElementById('timelineMonths');
    const months = Object.keys(AppState.newsletterData);

    timelineMonths.innerHTML = months.map((monthKey, index) => {
        const monthData = AppState.newsletterData[monthKey];
        const [monthName, year] = monthData.month.split(' ');
        const isActive = monthKey === AppState.currentMonth;

        return `
            <div class="timeline-month ${isActive ? 'active' : ''}" data-month="${monthKey}">
                <div class="timeline-month-name">${monthName}</div>
                <div class="timeline-month-year">${year}</div>
            </div>
        `;
    }).join('');

    // Add click handlers
    document.querySelectorAll('.timeline-month').forEach(element => {
        element.addEventListener('click', () => {
            const month = element.dataset.month;
            selectMonth(month);
        });
    });

    // Scroll buttons
    const scrollLeft = document.getElementById('timelineScrollLeft');
    const scrollRight = document.getElementById('timelineScrollRight');
    const timelineScroll = document.getElementById('timelineScroll');

    scrollLeft.addEventListener('click', () => {
        timelineScroll.scrollBy({ left: -200, behavior: 'smooth' });
    });

    scrollRight.addEventListener('click', () => {
        timelineScroll.scrollBy({ left: 200, behavior: 'smooth' });
    });
}

function selectMonth(monthKey) {
    if (AppState.currentMonth === monthKey) return;

    AppState.currentMonth = monthKey;

    // Update active month in timeline
    document.querySelectorAll('.timeline-month').forEach(element => {
        element.classList.remove('active');
        if (element.dataset.month === monthKey) {
            element.classList.add('active');
            // Scroll to active month
            element.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        }
    });

    // Update dashboard content
    updateDashboard();
}

// =============================================================================
// Dashboard Update
// =============================================================================

function updateDashboard() {
    const monthData = AppState.newsletterData[AppState.currentMonth];

    // Update period title
    document.getElementById('currentPeriod').textContent = monthData.month;

    // Update stats with animation
    updateStats(monthData.stats);

    // Update charts
    updateCharts(monthData);

    // Update highlights
    updateHighlights(monthData.highlights);

    // Update events
    updateEvents(monthData.events);

    // Add fade-in animation to main content
    document.querySelector('.dashboard-main').classList.remove('fade-in');
    void document.querySelector('.dashboard-main').offsetWidth; // Trigger reflow
    document.querySelector('.dashboard-main').classList.add('fade-in');
}

// =============================================================================
// Animated Statistics Counter
// =============================================================================

function updateStats(stats) {
    const statElements = [
        { selector: '.stat-card:nth-child(1) .stat-value', value: stats.schools },
        { selector: '.stat-card:nth-child(2) .stat-value', value: stats.teachers },
        { selector: '.stat-card:nth-child(3) .stat-value', value: stats.students },
        { selector: '.stat-card:nth-child(4) .stat-value', value: stats.apaar_ids }
    ];

    statElements.forEach(({ selector, value }) => {
        const element = document.querySelector(selector);
        if (element) {
            animateCounter(element, value);
        }
    });
}

function animateCounter(element, target) {
    const duration = 1500; // 1.5 seconds
    const start = 0;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Easing function (ease-out cubic)
        const easeProgress = 1 - Math.pow(1 - progress, 3);

        const current = Math.floor(start + (target - start) * easeProgress);
        element.textContent = formatNumber(current);

        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = formatNumber(target);
        }
    }

    requestAnimationFrame(update);
}

function formatNumber(num) {
    if (num >= 10000000) {
        return (num / 10000000).toFixed(1) + ' Cr';
    } else if (num >= 100000) {
        return (num / 100000).toFixed(1) + ' L';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toLocaleString('en-IN');
}

// =============================================================================
// Chart Visualizations
// =============================================================================

function initializeCharts() {
    // Trends Chart
    const trendsCtx = document.getElementById('trendsChart').getContext('2d');
    AppState.charts.trends = new Chart(trendsCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Attendance Rate (%)',
                    data: [],
                    borderColor: '#003d82',
                    backgroundColor: 'rgba(0, 61, 130, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Teacher Tracking (%)',
                    data: [],
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: getChartOptions('Percentage')
    });

    // State Performance Chart
    const stateCtx = document.getElementById('stateChart').getContext('2d');
    AppState.charts.state = new Chart(stateCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Attendance Rate (%)',
                    data: [],
                    backgroundColor: '#003d82'
                },
                {
                    label: 'APAAR Coverage (%)',
                    data: [],
                    backgroundColor: '#ff9933'
                }
            ]
        },
        options: getChartOptions('Percentage')
    });

    // Infrastructure Chart
    const infraCtx = document.getElementById('infrastructureChart').getContext('2d');
    AppState.charts.infrastructure = new Chart(infraCtx, {
        type: 'bar',
        data: {
            labels: ['Smart Classrooms', 'Computer Labs', 'Internet Enabled'],
            datasets: [{
                label: 'Count',
                data: [],
                backgroundColor: ['#003d82', '#17a2b8', '#28a745']
            }]
        },
        options: getChartOptions('Count')
    });

    // APAAR Chart
    const apaarCtx = document.getElementById('apaarChart').getContext('2d');
    AppState.charts.apaar = new Chart(apaarCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'APAAR IDs (Crores)',
                data: [],
                borderColor: '#ff9933',
                backgroundColor: 'rgba(255, 153, 51, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: getChartOptions('Crores')
    });
}

function getChartOptions(yAxisLabel) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    font: {
                        family: 'Inter',
                        size: 12
                    },
                    padding: 15,
                    usePointStyle: true
                }
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                padding: 12,
                titleFont: {
                    family: 'Inter',
                    size: 14
                },
                bodyFont: {
                    family: 'Inter',
                    size: 13
                },
                cornerRadius: 6
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                },
                ticks: {
                    font: {
                        family: 'Inter',
                        size: 11
                    }
                },
                title: {
                    display: true,
                    text: yAxisLabel,
                    font: {
                        family: 'Inter',
                        size: 12,
                        weight: 600
                    }
                }
            },
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    font: {
                        family: 'Inter',
                        size: 11
                    }
                }
            }
        },
        animation: {
            duration: 1000,
            easing: 'easeOutQuart'
        }
    };
}

function updateCharts(monthData) {
    // Get historical data for trends
    const months = Object.keys(AppState.newsletterData);
    const currentIndex = months.indexOf(AppState.currentMonth);
    const historicalMonths = months.slice(0, currentIndex + 1);

    // Update Trends Chart
    const trendsLabels = historicalMonths.map(m => {
        const [month] = AppState.newsletterData[m].month.split(' ');
        return month.substring(0, 3);
    });
    const attendanceData = historicalMonths.map(m => AppState.newsletterData[m].stats.attendance_rate);
    const teacherData = historicalMonths.map(m => AppState.newsletterData[m].stats.teacher_tracking);

    AppState.charts.trends.data.labels = trendsLabels;
    AppState.charts.trends.data.datasets[0].data = attendanceData;
    AppState.charts.trends.data.datasets[1].data = teacherData;
    AppState.charts.trends.update();

    // Update State Performance Chart
    const statePerf = monthData.state_performance;
    const stateNames = Object.keys(statePerf);
    const stateAttendance = stateNames.map(s => statePerf[s].attendance);
    const stateApaar = stateNames.map(s => statePerf[s].apaar_coverage);

    AppState.charts.state.data.labels = stateNames;
    AppState.charts.state.data.datasets[0].data = stateAttendance;
    AppState.charts.state.data.datasets[1].data = stateApaar;
    AppState.charts.state.update();

    // Update Infrastructure Chart
    const infra = monthData.infrastructure;
    AppState.charts.infrastructure.data.datasets[0].data = [
        infra.smart_classrooms,
        infra.computer_labs,
        infra.internet_enabled
    ];
    AppState.charts.infrastructure.update();

    // Update APAAR Chart
    const apaarLabels = historicalMonths.map(m => {
        const [month] = AppState.newsletterData[m].month.split(' ');
        return month.substring(0, 3);
    });
    const apaarData = historicalMonths.map(m => AppState.newsletterData[m].stats.apaar_ids / 10000000);

    AppState.charts.apaar.data.labels = apaarLabels;
    AppState.charts.apaar.data.datasets[0].data = apaarData;
    AppState.charts.apaar.update();
}

// =============================================================================
// Highlights & Events
// =============================================================================

function updateHighlights(highlights) {
    const highlightsGrid = document.getElementById('highlightsGrid');
    highlightsGrid.innerHTML = highlights.map(highlight => `
        <div class="highlight-card fade-in">
            <p>${highlight}</p>
        </div>
    `).join('');
}

function updateEvents(events) {
    const eventsGrid = document.getElementById('eventsGrid');
    eventsGrid.innerHTML = events.map(event => `
        <div class="event-card fade-in">
            <div class="event-date">${event.date}</div>
            <h4>${event.title}</h4>
            <p>${event.description}</p>
        </div>
    `).join('');
}

// =============================================================================
// Chatbot
// =============================================================================

function initializeChatbot() {
    const chatbotToggle = document.getElementById('chatbotToggle');
    const chatbotWindow = document.getElementById('chatbotWindow');
    const chatbotClose = document.getElementById('chatbotClose');
    const chatbotSend = document.getElementById('chatbotSend');
    const chatbotInput = document.getElementById('chatbotInput');

    chatbotToggle.addEventListener('click', () => {
        chatbotWindow.classList.add('active');
        chatbotInput.focus();
    });

    chatbotClose.addEventListener('click', () => {
        chatbotWindow.classList.remove('active');
    });

    chatbotSend.addEventListener('click', () => {
        sendMessage();
    });

    chatbotInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
}

async function sendMessage() {
    const input = document.getElementById('chatbotInput');
    const message = input.value.trim();

    if (!message) return;

    // Add user message
    addMessage(message, 'user');
    input.value = '';

    // Show loading
    addLoadingMessage();

    try {
        // Call backend API
        const response = await fetch(`${AppState.apiBaseUrl}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: message,
                current_month: AppState.currentMonth
            })
        });

        const data = await response.json();

        // Remove loading
        removeLoadingMessage();

        // Add assistant response
        addMessage(data.response, 'assistant');

        // Check if visualization is needed
        if (data.visualization) {
            handleVisualization(data.visualization);
        }
    } catch (error) {
        console.error('Error sending message:', error);
        removeLoadingMessage();
        addMessage('I apologize, but I am currently unable to process your request. Please ensure the backend server is running.', 'assistant');
    }
}

function addMessage(content, type) {
    const messagesContainer = document.getElementById('chatbotMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.innerHTML = `<div class="message-content">${content}</div>`;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function addLoadingMessage() {
    const messagesContainer = document.getElementById('chatbotMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message loading';
    messageDiv.id = 'loadingMessage';
    messageDiv.innerHTML = `
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function removeLoadingMessage() {
    const loadingMessage = document.getElementById('loadingMessage');
    if (loadingMessage) {
        loadingMessage.remove();
    }
}

function handleVisualization(vizData) {
    // Handle query-to-visualization mode
    if (vizData.type === 'chart') {
        // Scroll to relevant chart and highlight it
        const chartCard = document.querySelector(`#${vizData.chartId}`).closest('.chart-card');
        chartCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
        chartCard.style.boxShadow = '0 0 0 3px #ff9933';
        setTimeout(() => {
            chartCard.style.boxShadow = '';
        }, 2000);
    }
}

// =============================================================================
// Initialization
// =============================================================================

async function initialize() {
    // Load data
    await loadNewsletterData();

    if (!AppState.newsletterData) {
        console.error('Failed to load newsletter data');
        return;
    }

    // Initialize components
    initializeTimeline();
    initializeCharts();
    initializeChatbot();

    // Initial dashboard update
    updateDashboard();

    console.log('Education Intelligence Dashboard initialized successfully');
}

// Start application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}
