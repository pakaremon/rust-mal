function submitForm() {
    resetReport();

    const loader = document.getElementById('loader');
    loader.classList.remove('hidden');

    const form = document.getElementById('submitForm');
    const formData = new FormData(form);



    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken') // Include CSRF token for security
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        // Handle success (e.g., update the UI with the response data)
            displayReport(data.sources);
       
    })
    .catch((error) => {
        console.error('Error:', error);
        // Handle error
    })
    .finally(() => {
        // Hide the loader
    //   check if loader is not hidden
        if (!loader.classList.contains('hidden')) {
            loader.classList.add('hidden');
        };
    });

}

function submitDynamicAnalysisForm() {
   

    const loader = document.getElementById('loader');
    loader.classList.remove('hidden');

    const form = document.getElementById('submitForm');
    const formData = new FormData(form);



    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken') // Include CSRF token for security
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        // Handle success (e.g., update the UI with the response data)

        displayDynamicReport(data);

    })
    .catch((error) => {
        console.error('Error:', error);
        // Handle error
    })
    .finally(() => {
        // Hide the loader
    //   check if loader is not hidden
        if (!loader.classList.contains('hidden')) {
            loader.classList.add('hidden');
        };
    });

}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function displayDynamicReport(data) {
    const feedbackPanel = document.getElementById('feedback-panel');
    feedbackPanel.classList.remove('hidden');

    // Combine install and execute phases, removing duplicates
    const combinedReport = {
        num_files: data.dynamic_analysis_report.install.num_files + data.dynamic_analysis_report.execute.num_files,
        num_commands: data.dynamic_analysis_report.install.num_commands + data.dynamic_analysis_report.execute.num_commands,
        num_network_connections: data.dynamic_analysis_report.install.num_network_connections + data.dynamic_analysis_report.execute.num_network_connections,
        num_system_calls: data.dynamic_analysis_report.install.num_system_calls + data.dynamic_analysis_report.execute.num_system_calls,
        files: {
            read: [...new Set([...data.dynamic_analysis_report.install.files.read, ...data.dynamic_analysis_report.execute.files.read])],
            write: [...new Set([...data.dynamic_analysis_report.install.files.write, ...data.dynamic_analysis_report.execute.files.write])],
            delete: [...new Set([...data.dynamic_analysis_report.install.files.delete, ...data.dynamic_analysis_report.execute.files.delete])]
        },
        dns: [...new Set([...data.dynamic_analysis_report.install.dns, ...data.dynamic_analysis_report.execute.dns])],
        ips: [...new Map([...data.dynamic_analysis_report.install.ips, ...data.dynamic_analysis_report.execute.ips].map(ip => [JSON.stringify(ip), ip])).values()],
        commands: [...new Set([...data.dynamic_analysis_report.install.commands, ...data.dynamic_analysis_report.execute.commands])],
        syscalls: Object.entries({
            ...data.dynamic_analysis_report.install.syscalls,
            ...data.dynamic_analysis_report.execute.syscalls
        }).reduce((acc, [key, value]) => {
            acc[key] = (data.dynamic_analysis_report.install.syscalls[key] || 0) + (data.dynamic_analysis_report.execute.syscalls[key] || 0);
            return acc;
        }, {})
    };

    feedbackPanel.innerHTML = `
        <div class="bg-white shadow rounded-lg p-6 max-w-lg mx-auto">
            <h1>Report Detail</h1>
            <div class="report-details">
                <h2>Package Information</h2>
                <ul>
                    <li><strong>Package Name:</strong> ${data.dynamic_analysis_report.packages.package_name}</li>
                    <li><strong>Package Version:</strong> ${data.dynamic_analysis_report.packages.package_version}</li>
                    <li><strong>Ecosystem:</strong> ${data.dynamic_analysis_report.packages.ecosystem}</li>
                </ul>

                <h2>Analysis Summary</h2>
                <ul>
                    <li><strong>Number of Files:</strong> ${combinedReport.num_files}</li>
                    <li><strong>Number of Commands:</strong> ${combinedReport.num_commands}</li>
                    <li><strong>Number of Network Connections:</strong> ${combinedReport.num_network_connections}</li>
                    <li><strong>Number of System Calls:</strong> ${combinedReport.num_system_calls}</li>
                </ul>

                <h2>Files</h2>
                <ul>
                    <li><strong>Opened Files:</strong>
                        <div class="collapsible">
                            <ul>
                                ${combinedReport.files.read.length > 0 ? combinedReport.files.read.map(path => `<li>${path}</li>`).join('') : '<li>No files read</li>'}
                            </ul>
                        </div>
                        <button class="toggle-btn">Show More</button>
                    </li>
                    <li><strong>Deleted Files:</strong>
                        <div class="collapsible">
                            <ul>
                                ${combinedReport.files.delete.length > 0 ? combinedReport.files.delete.map(path => `<li>${path}</li>`).join('') : '<li>No files deleted</li>'}
                            </ul>
                        </div>
                        <button class="toggle-btn">Show More</button>
                    </li>
                    <li><strong>Written Files:</strong>
                        <div class="collapsible">
                            <ul>
                                ${combinedReport.files.write.length > 0 ? combinedReport.files.write.map(path => `<li>${path}</li>`).join('') : '<li>No files written</li>'}
                            </ul>
                        </div>
                        <button class="toggle-btn">Show More</button>
                    </li>
                </ul>

                <h2>DNS Queries</h2>
                <ul>
                    ${combinedReport.dns.length > 0 ? combinedReport.dns.map(hostname => `<li>${hostname}</li>`).join('') : '<li>No DNS queries</li>'}
                </ul>

                <h2>IP Connections</h2>
                <ul>
                    ${combinedReport.ips.length > 0 ? combinedReport.ips.map(ip => `
                        <li><strong>Address:</strong> ${ip.Address}, <strong>Port:</strong> ${ip.Port}${ip.Hostnames ? `, <strong>Hostname:</strong> ${ip.Hostnames}` : ''}</li>
                    `).join('') : '<li>No IP connections</li>'}
                </ul>

                <h2>Executed Commands</h2>
                <div class="collapsible">
                    <ul>
                        ${combinedReport.commands.length > 0 ? combinedReport.commands.map(command => `<li>${command}</li>`).join('') : '<li>No commands executed</li>'}
                    </ul>
                </div>
                <button class="toggle-btn">Show More</button>

                <h2>System Calls</h2>
                <div class="collapsible">
                    <ul>
                        ${Object.entries(combinedReport.syscalls).map(([syscall, count]) => `<li>${syscall} : ${count}</li>`).join('')}
                    </ul>
                </div>
                <button class="toggle-btn">Show More</button>
            </div>
        </div>
    `;
}

/**
 * function to display the report in the feedback panel
 * @param {*} data 
 */
function displayReport(data) {

    
    const feedbackPanel = document.getElementById('feedback-panel');
    const loadingSpinner = document.getElementById('loading-spinner');
    const analysisResult = document.getElementById('analysis-result');
    const errorMessage = document.getElementById('error-message');
    
    // check if data is not empty list
    if (data.length > 0) {
        feedbackPanel.classList.remove('hidden');
        loadingSpinner.classList.add('hidden');
        analysisResult.classList.remove('hidden');

        const resultSummary = document.getElementById('result-summary');
        resultSummary.innerHTML = ''; // Clear previous results
        data.forEach((item, index) => {
            const p = document.createElement('p');
            p.textContent = `${index + 1}: ${item}`;
            resultSummary.appendChild(p);
        });
    } else {
        feedbackPanel.classList.remove('hidden');
        loadingSpinner.classList.add('hidden');
        analysisResult.classList.add('hidden');
        errorMessage.classList.remove('hidden');
    }
}



/**
 * function to reset the report, everytime the form is submitted
 * @returns {void}
 */
function resetReport() {
    const feedbackPanel = document.getElementById('feedback-panel');
    const loadingSpinner = document.getElementById('loading-spinner');
    const analysisResult = document.getElementById('analysis-result');
    const errorMessage = document.getElementById('error-message');
    
    feedbackPanel.classList.add('hidden');
    loadingSpinner.classList.add('hidden');
    analysisResult.classList.add('hidden');
    errorMessage.classList.add('hidden');
}

/**
 * function to display the dynamic report in the feedback panel
 * @returns {void}
 */

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".toggle-btn").forEach(function (btn) {
        btn.addEventListener("click", function () {
            let content = this.previousElementSibling;
            if (content.style.maxHeight === "150px") {
                content.style.maxHeight = content.scrollHeight + "px"; // Expand
                content.style.padding = "10px"; // Add padding when expanded
                this.textContent = "Show Less";
            } else {
                content.style.maxHeight = "150px"; // Collapse
                content.style.padding = "10px"; // Keep padding when collapsed
                this.textContent = "Show More";
            }
        });
    });
});