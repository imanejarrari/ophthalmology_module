/** @odoo-module **/

import { Component, useState } from '@odoo/owl';
import { xml } from '@odoo/owl';
import { registry } from '@web/core/registry';  // Import the registry

class OphthalmologyDashboard extends Component {
    state = useState({
        total_patients: 0,
        new_patients: 0,
        old_patients: 0,
        today_appointments: [],
    });

    async willStart() {
        const dashboardData = await this.env.services.orm.call(
            'ophthalmology.patient',
            'get_dashboard_data',
            []
        );

        this.state.total_patients = dashboardData.total_patients;
        this.state.new_patients = dashboardData.new_patients;
        this.state.old_patients = dashboardData.old_patients;
        this.state.today_appointments = dashboardData.today_appointments;
    }

    static template = xml/* xml */`
        <div class="oe_structure">
            <h1>Ophthalmology Dashboard</h1>
            <div class="row mt-3 mb-3">
                <div class="col-md-3">
                    <div class="card text-white bg-success">
                        <div class="card-body">
                            <h5>Total Patients</h5>
                            <h2><t t-esc="state.total_patients"/></h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-white bg-primary">
                        <div class="card-body">
                            <h5>New Patients</h5>
                            <h2><t t-esc="state.new_patients"/></h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card text-white bg-info">
                        <div class="card-body">
                            <h5>Old Patients</h5>
                            <h2><t t-esc="state.old_patients"/></h2>
                        </div>
                    </div>
                </div>
            </div>

            <h3>Today's Appointments</h3>
            <ul>
                <t t-foreach="state.today_appointments" t-as="appt" t-key="appt.patient_name">
                    <li><t t-esc="appt.patient_name"/> - <t t-esc="appt.time"/></li>
                </t>
            </ul>
        </div>
    `;
}

// Register the component in the actions registry
registry.category('actions').add('ophthalmology.OphthalmologyDashboard', OphthalmologyDashboard);

// Export the OWL component
export { OphthalmologyDashboard };
