import { Component, useState, onWillStart, onMounted, onWillUnmount } from '@odoo/owl';
import { xml } from '@odoo/owl';
import { registry } from '@web/core/registry';
import { useService } from '@web/core/utils/hooks';

class OphthalmologyDashboard extends Component {
    setup() {
        this.state = useState({
            total_patients: 0,
            new_patients: 0,
            total_appointments: 0,
            today_appointments: [],
            upcoming_appointments: [],
            missed_appointments: 0,
            total_revenue: 0,
            monthly_revenue: 0,
            weekly_revenue: 0,
            yearly_revenue: 0,
            average_examination_price: 0,
            loading: true,
            chartPeriod: 'monthly', 
            appointmentChartPeriod: 'monthly', 
            currentDate: new Date().toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'numeric',
                day: 'numeric'
            })
        });
        
        this.orm = useService("orm");
        this.chart = null;
        this.appointmentChart = null;
        this.refreshInterval = null;
        
        onWillStart(async () => {
            await this.fetchDashboardData();
        });
        
        onMounted(() => {
            setTimeout(() => {
                this.initRevenueChart();
                this.initAppointmentChart();
                this.initCircularProgress();
            }, 100);
            
            this.refreshInterval = setInterval(() => {
                this.fetchDashboardData();
            }, 5 * 60 * 1000);
        });
        
        onWillUnmount(() => {
            if (this.refreshInterval) {
                clearInterval(this.refreshInterval);
            }
        });
    }
    
    async fetchDashboardData() {
        try {
            this.state.loading = true;
            const data = await this.orm.call(
                'ophthalmology.patient',
                'get_dashboard_data',
                []
            );
            
            
            Object.assign(this.state, {
                total_patients: data.total_patients || 0,
                new_patients: data.new_patients || 0,
                total_appointments: data.total_appointments || 0,
                today_appointments: data.today_appointments || [],
                upcoming_appointments: data.upcoming_appointments || [],
                missed_appointments: data.missed_appointments || 0,
                total_revenue: data.total_revenue || 0,
                monthly_revenue: data.monthly_revenue || 0,
                weekly_revenue: data.weekly_revenue || 0,
                yearly_revenue: data.yearly_revenue || 0,
                average_examination_price: data.average_examination_price || 0,
                loading: false
            });
            
            if (data.weekly_revenue_data && data.weekly_revenue_data.values) {
                console.log("Weekly revenue data:", data.weekly_revenue_data); // Debug log
                this.state.weekly_revenue_data = data.weekly_revenue_data;
            }
            
            if (data.monthly_revenue_data && data.monthly_revenue_data.values) {
                console.log("Monthly revenue data:", data.monthly_revenue_data); // Debug log
                this.state.monthly_revenue_data = data.monthly_revenue_data;
            }
            
            if (data.yearly_revenue_data && data.yearly_revenue_data.values) {
                console.log("Yearly revenue data:", data.yearly_revenue_data); // Debug log
                this.state.yearly_revenue_data = data.yearly_revenue_data;
            }
            
            if (data.weekly_appointment_data && data.weekly_appointment_data.values) {
                console.log("Weekly appointment data:", data.weekly_appointment_data);
                this.state.weekly_appointment_data = data.weekly_appointment_data;
            }
            
            if (data.monthly_appointment_data && data.monthly_appointment_data.values) {
                console.log("Monthly appointment data:", data.monthly_appointment_data);
                this.state.monthly_appointment_data = data.monthly_appointment_data;
            }
            
            if (data.yearly_appointment_data && data.yearly_appointment_data.values) {
                console.log("Yearly appointment data:", data.yearly_appointment_data);
                this.state.yearly_appointment_data = data.yearly_appointment_data;
            }
            
          setTimeout(() => {
            this.initRevenueChart();
            this.initAppointmentChart();
            this.initCircularProgress();
        }, 100);
    } catch (error) {
        console.error("Failed to fetch dashboard data:", error);
        this.state.loading = false;
    }
    }
    
    getInitials(name) {
        if (!name) return '';
        
        return name
            .split(' ')
            .map(part => part.charAt(0))
            .join('')
            .toUpperCase()
            .substring(0, 2);
    }
    
    initRevenueChart() {
        const chartCanvas = document.getElementById('revenueChart');
        if (!chartCanvas) {
            console.error("Chart canvas not found");
            return;
        }
        
        if (this.chart) {
            this.chart.destroy();
        }
        
        let labels, data;
        if (this.state.chartPeriod === 'weekly') {
            labels = this.state.weekly_revenue_data?.labels || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
            data = this.state.weekly_revenue_data?.values || [0, 0, 0, 0, 0, 0, 0];
            console.log("Using weekly data:", labels, data); // Debug log
        } else if (this.state.chartPeriod === 'yearly') {
            labels = this.state.yearly_revenue_data?.labels || ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            data = this.state.yearly_revenue_data?.values || [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
            console.log("Using yearly data:", labels, data); // Debug log
        } else {
            labels = this.state.monthly_revenue_data?.labels || ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
            data = this.state.monthly_revenue_data?.values || [0, 0, 0, 0];
            console.log("Using monthly data:", labels, data); // Debug log
        }
        
        const ctx = chartCanvas.getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(123, 198, 123, 0.2)');
        gradient.addColorStop(1, 'rgba(123, 198, 123, 0)');
        
        this.chart = new Chart(chartCanvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Revenue',
                    data: data,
                    backgroundColor: gradient,
                    borderColor: '#7bc67b',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#7bc67b',
                    pointBorderColor: '#fff',
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            drawBorder: false,
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            font: {
                                size: 10
                            },
                            color: '#6c757d'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 10
                            },
                            color: '#6c757d'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(255, 255, 255, 0.9)',
                        titleColor: '#333',
                        bodyColor: '#333',
                        borderColor: '#e0e0e0',
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return `Revenue: ${context.parsed.y} DH`;
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }

    initCircularProgress() {
        const progressElement = document.querySelector('.circular-progress');
        if (!progressElement) return;
        
        let completionPercentage = 78; 
        
        if (this.state.total_appointments > 0) {
            const missedAppointments = this.state.missed_appointments || 0;
            const completedAppointments = this.state.total_appointments - missedAppointments;
            completionPercentage = Math.round((completedAppointments / this.state.total_appointments) * 100);
        }
        
        progressElement.style.setProperty('--percentage', completionPercentage);
        
        const progressText = progressElement.querySelector('.progress-text');
        if (progressText) {
            progressText.textContent = `${completionPercentage}%`;
        }
    }

    changeChartPeriod(period) {
        this.state.chartPeriod = period;
        this.initRevenueChart();
    }

    initAppointmentChart() {
        const chartCanvas = document.getElementById('appointmentChart');
        if (!chartCanvas) {
            console.error("Appointment chart canvas not found");
            return;
        }
        
        if (this.appointmentChart) {
            this.appointmentChart.destroy();
        }
        
        let labels, data;
        if (this.state.appointmentChartPeriod === 'weekly') {
            labels = this.state.weekly_appointment_data?.labels || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
            data = this.state.weekly_appointment_data?.values || [0, 0, 0, 0, 0, 0, 0];
        } else if (this.state.appointmentChartPeriod === 'yearly') {
            labels = this.state.yearly_appointment_data?.labels || ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            data = this.state.yearly_appointment_data?.values || [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
        } else {
            labels = this.state.monthly_appointment_data?.labels || ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
            data = this.state.monthly_appointment_data?.values || [0, 0, 0, 0];
        }
        
        const ctx = chartCanvas.getContext('2d');
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(123, 104, 238, 0.2)'); 
        gradient.addColorStop(1, 'rgba(123, 104, 238, 0)');
        
        this.appointmentChart = new Chart(chartCanvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Appointments',
                    data: data,
                    backgroundColor: gradient,
                    borderColor: '#7b68ee', 
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#7b68ee',
                    pointBorderColor: '#fff',
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            drawBorder: false,
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            font: {
                                size: 10
                            },
                            color: '#6c757d'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 10
                            },
                            color: '#6c757d'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(255, 255, 255, 0.9)',
                        titleColor: '#333',
                        bodyColor: '#333',
                        borderColor: '#e0e0e0',
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return `Appointments: ${context.parsed.y}`;
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }

    changeAppointmentChartPeriod(period) {
        this.state.appointmentChartPeriod = period;
        this.initAppointmentChart();
    }
    async onViewAllClick(ev) {
       ev.preventDefault();
     this.env.services.action.doAction("ophthalmology.ophthalmology_action_appointments");
    }

    

    static template = xml/* xml */`
        <div class="ophthalmology-dashboard">
            <div t-if="state.loading" class="text-center py-5">
                <i class="fa fa-spinner fa-spin fa-2x"></i>
                <p>Loading dashboard data...</p>
            </div>
            
            <div t-else="" class="dashboard-content">
                <!-- Top Section: Stats Cards Only -->
                <div class="top-section">
                    <div class="stats-container">
                        <div class="stats-section">
                            <!-- Circular Progress -->
                            <div class="stats-card text-center">
                                <div class="circular-progress" style="--percentage: 78;">
                                    <svg viewBox="0 0 100 100">
                                        <circle class="progress-background" cx="50" cy="50" r="45"></circle>
                                        <circle class="progress-value" cx="50" cy="50" r="45"></circle>
                                    </svg>
                                    <div class="progress-text">78%</div>
                                </div>
                                <p class="mt-2 mb-0 text-muted">Appointment Completion</p>
                            </div>
                            
                            <!-- New Patients -->
                            <div class="stats-card">
                                <h5 class="card-title">New patients</h5>
                                <h2 class="stats-value"><t t-esc="state.new_patients"/></h2>
                                <div class="stats-indicator up">
                                    <i class="fa fa-arrow-up mr-1"></i>
                                    <span>+5% from last month</span>
                                </div>
                            </div>
                            
                            <!-- Total Patients -->
                            <div class="stats-card">
                                <h5 class="card-title">Total patients</h5>
                                <h2 class="stats-value"><t t-esc="state.total_patients"/></h2>
                                <div class="stats-indicator up">
                                    <i class="fa fa-arrow-up mr-1"></i>
                                    <span>+2% from last month</span>
                                </div>
                            </div>
                            
                            <!-- Total Revenue -->
                            <div class="stats-card">
                                <h5 class="card-title">Total Revenue</h5>
                                <h2 class="stats-value"><t t-esc="state.total_revenue"/> DH</h2>
                                <div class="stats-indicator up">
                                    <i class="fa fa-arrow-up mr-1"></i>
                                    <span>+8% from last month</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- middle Section: Charts -->
                <div class="middle-section">
                    <div class="charts-row">
                        <!-- Revenue Chart -->
                        <div class="chart-column">
                            <div class="chart-card">
                                <div class="card-header">
                                    <h5 class="card-title">Revenue Statistics</h5>
                                    <div class="chart-period-selector">
                                        <button t-attf-class="btn btn-sm {{state.chartPeriod === 'weekly' ? 'btn-primary' : 'btn-outline-secondary'}}" 
                                                t-on-click="() => this.changeChartPeriod('weekly')">Weekly</button>
                                        <button t-attf-class="btn btn-sm {{state.chartPeriod === 'monthly' ? 'btn-primary' : 'btn-outline-secondary'}}" 
                                                t-on-click="() => this.changeChartPeriod('monthly')">Monthly</button>
                                        <button t-attf-class="btn btn-sm {{state.chartPeriod === 'yearly' ? 'btn-primary' : 'btn-outline-secondary'}}" 
                                                t-on-click="() => this.changeChartPeriod('yearly')">Yearly</button>
                                    </div>
                                </div>
                                <div class="chart-container">
                                    <canvas id="revenueChart" width="400" height="200"></canvas>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Appointments Chart -->
                        <div class="chart-column">
                            <div class="chart-card">
                                <div class="card-header">
                                    <h5 class="card-title">Appointments Over Time</h5>
                                    <div class="chart-period-selector">
                                        <button t-attf-class="btn btn-sm {{state.appointmentChartPeriod === 'weekly' ? 'btn-primary' : 'btn-outline-secondary'}}" 
                                                t-on-click="() => this.changeAppointmentChartPeriod('weekly')">Weekly</button>
                                        <button t-attf-class="btn btn-sm {{state.appointmentChartPeriod === 'monthly' ? 'btn-primary' : 'btn-outline-secondary'}}" 
                                                t-on-click="() => this.changeAppointmentChartPeriod('monthly')">Monthly</button>
                                        <button t-attf-class="btn btn-sm {{state.appointmentChartPeriod === 'yearly' ? 'btn-primary' : 'btn-outline-secondary'}}" 
                                                t-on-click="() => this.changeAppointmentChartPeriod('yearly')">Yearly</button>
                                    </div>
                                </div>
                                <div class="chart-container">
                                    <canvas id="appointmentChart" width="400" height="200"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- bottom Section: Appointments -->
                <div class="bottom-section">
                    <!-- Today's Appointments -->
                    <div class="appointments-column">
                        <div class="appointments-card">
                            <div class="card-header">
                                <h5 class="card-title">Today's Appointments </h5>
                               <a t-on-click="onViewAllClick" href="#" class="view-all">View all</a>
                            </div>
                            <div class="card-body p-0">
                                <div t-if="state.today_appointments.length === 0" class="text-center py-3 text-muted">
                                    No appointments scheduled for today
                                </div>
                                <div t-else="" class="appointments-list">
                                    <t t-foreach="state.today_appointments" t-as="appt" t-key="appt.id">
                                        <div class="appointment-item">
                                            <div class="appointment-time">
                                                <t t-esc="appt.time"/>
                                            </div>
                                            <div class="appointment-patient">
                                                <div class="patient-avatar">
                                                    <t t-esc="this.getInitials(appt.patient_name)"/>
                                                </div>
                                                <div class="patient-info">
                                                    <div class="patient-name">
                                                        <t t-esc="appt.patient_name"/>
                                                    </div>
                                                    <div class="appointment-purpose">
                                                        <t t-esc="appt.purpose || 'General checkup'"/>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="appointment-actions">
                                                <button title="View details">
                                                    <i class="fa fa-eye"></i>
                                                </button>
                                            </div>
                                        </div>
                                    </t>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Upcoming Appointments -->
                    <div class="appointments-column">
                        <div class="appointments-card">
                            <div class="card-header">
                                <h5 class="card-title">Upcoming appointments</h5>
                                 <a t-on-click="onViewAllClick" href="#" class="view-all">View all</a>
                            </div>
                            <div class="card-body p-0">
                                <div t-if="state.upcoming_appointments.length === 0" class="text-center py-3 text-muted">
                                    No upcoming appointments
                                </div>
                                <div t-else="" class="appointments-list">
                                    <t t-foreach="state.upcoming_appointments" t-as="appt" t-key="appt.id">
                                        <div class="appointment-item">
                                            <div class="appointment-time">
                                                <t t-esc="appt.date"/>
                                            </div>
                                            <div class="appointment-patient">
                                                <div class="patient-avatar">
                                                    <t t-esc="this.getInitials(appt.patient_name)"/>
                                                </div>
                                                <div class="patient-info">
                                                    <div class="patient-name">
                                                        <t t-esc="appt.patient_name"/>
                                                    </div>
                                                    <div class="appointment-purpose">
                                                        <t t-esc="appt.time"/> - <t t-esc="appt.purpose || 'General checkup'"/>
                                                    </div>
                                                </div>
                                            </div>
                                            <div class="appointment-actions">
                                                <button title="View details">
                                                    <i class="fa fa-eye"></i>
                                                </button>
                                           

                                          </div>
                                        </div>
                                    </t>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    static components = { }; 
}

registry.category('actions').add('ophthalmology.OphthalmologyDashboard', OphthalmologyDashboard);

export { OphthalmologyDashboard };
