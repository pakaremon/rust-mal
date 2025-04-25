function submitForm() {

    const loader = document.getElementById('loader');
    loader.classList.remove('d-none');

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
        displayReport(data);
       
    })
    .catch((error) => {
        console.error('Error:', error);
        // Handle error
    })
    .finally(() => {
        // Hide the loader
    //   check if loader is not hidden
        if (!loader.classList.contains('d-none')) {
            loader.classList.add('d-none');
        };
    });

}

function submitDynamicAnalysisForm() {
   
    showLoader();

    const form = document.getElementById('dynamicForm');
    const formData = new FormData(form);



    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken') // Include CSRF token for security
        }
    })
    .then(response => {
        if (response.headers.get('Content-Type')?.includes('application/json')) {
            return response.json();
        } else {
            throw new Error('Invalid JSON response');
        }
    })
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
        hideLoader();
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
    feedbackPanel.classList.remove('d-none');

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
        <div class="<div report-details card shadow-lg">
            <div class="card-header bg-primary text-white">
                <h1 class="card-title">Report Detail</h1>
            </div>
            <div class="card-body">
                <h2 class="h5">Package Information</h2>
                <ul class="list-group mb-3">
                    <li class="list-group-item"><strong>Package Name:</strong> ${data.dynamic_analysis_report.packages.package_name}</li>
                    <li class="list-group-item"><strong>Package Version:</strong> ${data.dynamic_analysis_report.packages.package_version}</li>
                    <li class="list-group-item"><strong>Ecosystem:</strong> ${data.dynamic_analysis_report.packages.ecosystem}</li>
                </ul>

                <h2 class="h5">Analysis Summary</h2>
                <ul class="list-group mb-3">
                    <li class="list-group-item"><strong>Number of Files:</strong> ${combinedReport.num_files}</li>
                    <li class="list-group-item"><strong>Number of Commands:</strong> ${combinedReport.num_commands}</li>
                    <li class="list-group-item"><strong>Number of Network Connections:</strong> ${combinedReport.num_network_connections}</li>
                    <li class="list-group-item"><strong>Number of System Calls:</strong> ${combinedReport.num_system_calls}</li>
                </ul>

                <h2 class="h5">Files</h2>
                <ul class="list-group mb-3">
                    <li class="list-group-item"><strong>Opened Files:</strong>
                        <div class="collapse" id="readFiles">
                            <ul>
                                ${combinedReport.files.read.length > 0 ? combinedReport.files.read.map(path => `<li>${path}</li>`).join('') : '<li>No files read</li>'}
                            </ul>
                        </div>
                        <button class="btn btn-link" data-bs-toggle="collapse" data-bs-target="#readFiles">Show More</button>
                    </li>
                    <li class="list-group-item"><strong>Deleted Files:</strong>
                        <div class="collapse" id="deletedFiles">
                            <ul>
                                ${combinedReport.files.delete.length > 0 ? combinedReport.files.delete.map(path => `<li>${path}</li>`).join('') : '<li>No files deleted</li>'}
                            </ul>
                        </div>
                        <button class="btn btn-link" data-bs-toggle="collapse" data-bs-target="#deletedFiles">Show More</button>
                    </li>
                    <li class="list-group-item"><strong>Written Files:</strong>
                        <div class="collapse" id="writtenFiles">
                            <ul>
                                ${combinedReport.files.write.length > 0 ? combinedReport.files.write.map(path => `<li>${path}</li>`).join('') : '<li>No files written</li>'}
                            </ul>
                        </div>
                        <button class="btn btn-link" data-bs-toggle="collapse" data-bs-target="#writtenFiles">Show More</button>
                    </li>
                </ul>

                <h2 class="h5">DNS Queries</h2>
                <ul class="list-group mb-3">
                    ${combinedReport.dns.length > 0 ? combinedReport.dns.map(hostname => `<li class="list-group-item">${hostname}</li>`).join('') : '<li class="list-group-item">No DNS queries</li>'}
                </ul>

                <h2 class="h5">IP Connections</h2>
                <ul class="list-group mb-3">
                    ${combinedReport.ips.length > 0 ? combinedReport.ips.map(ip => `
                        <li class="list-group-item"><strong>Address:</strong> ${ip.Address}, <strong>Port:</strong> ${ip.Port}${ip.Hostnames ? `, <strong>Hostname:</strong> ${ip.Hostnames}` : ''}</li>
                    `).join('') : '<li class="list-group-item">No IP connections</li>'}
                </ul>

                <h2 class="h5">Executed Commands</h2>
                <div class="collapse" id="executedCommands">
                    <ul>
                        ${combinedReport.commands.length > 0 ? combinedReport.commands.map(command => `<li>${command}</li>`).join('') : '<li>No commands executed</li>'}
                    </ul>
                </div>
                <button class="btn btn-link" data-bs-toggle="collapse" data-bs-target="#executedCommands">Show More</button>

                <h2 class="h5">System Calls</h2>
                <div class="collapse" id="systemCalls">
                    <ul>
                        ${Object.entries(combinedReport.syscalls).map(([syscall, count]) => `<li>${syscall} : ${count}</li>`).join('')}
                    </ul>
                </div>
                <button class="btn btn-link" data-bs-toggle="collapse" data-bs-target="#systemCalls">Show More</button>
            </div>
        </div>
    `;
}


function showLoader() {
//  remove class d-none from loader
    const loader = document.getElementById('loader');
    loader.classList.remove('d-none');
 
}

function hideLoader() {
//  add class d-none to loader
    const loader = document.getElementById('loader');
    loader.classList.add('d-none');
}


/**

 * Display the report in the feedback panel.
 * @param {Array} sources - The sources to display in the report.
 */
function displayReport(data) {
    const feedbackPanel = document.getElementById('feedback-panel');
    feedbackPanel.classList.remove('d-none');

    if (data.typosquatting_candidates) {
        const typosquattingCandidates = data.typosquatting_candidates.map(candidate => candidate || []).flat();
        feedbackPanel.innerHTML = `
            <div class="report-details card shadow-lg">
                <div class="card-header bg-primary text-white">
                    <h1 class="card-title">Report Detail</h1>
                </div>
                <div class="card-body">
                    <h2 class="h5">Typosquatting Candidates</h2>
                    <ul class="list-group mb-3">
                        ${typosquattingCandidates.length > 0 
                            ? typosquattingCandidates.map(candidate => `<li class="list-group-item">${candidate}</li>`).join('') 
                            : '<li class="list-group-item">No typosquatting candidates found</li>'}
                    </ul>
                </div>
            </div>
        `;
    }

    if (data.source_urls) {
        const sources = data.source_urls.map(source => source || []).flat();
        feedbackPanel.innerHTML = `
            <div class="report-details card shadow-lg">
                <div class="card-header bg-primary text-white">
                    <h1 class="card-title">Report Detail</h1>
                </div>
                <div class="card-body">
                    <h2 class="h5">Source URLs</h2>
                    <ul class="list-group mb-3">
                        ${sources.length > 0 
                            ? sources.map(source => `<li class="list-group-item">${source}</li>`).join('') 
                            : '<li class="list-group-item">No source URLs found</li>'}
                    </ul>
                </div>
            </div>
        `;
    }
}
      
function submitLastPyMile() {
    showLoader();
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
        displayLastbyMileReport(data.lastpymile_report);
    })
    .catch((error) => {
        console.error('Error:', error);
        // Handle error
    })
    .finally(() => {
        // Hide the loader
        hideLoader();
    });
}

function displayLastbyMileReport(data) {


        const feedbackPanel = document.getElementById('feedback-panel');
        feedbackPanel.classList.remove('d-none');
        let reportHTML = `            
        <div class="report-details card shadow-lg">
            <div class="card-header bg-primary text-white">
                <h1 class="card-title">Report Detail</h1>
            </div>
            <div class="card-body">
               <h2 class="h5">Package Name: ${data.package.name}</h2>
                <h2 class="h5">Package Version: ${data.package.version}</h2>
                <h2>Files Modified in Releases Flagged by Bandit Tool</h2>`;

        data.results.forEach(dt => {
            reportHTML += `<h3>Release: ${dt.release}</h3>`;
            const risks = ['phantom_files', 'low_risk_files', 'medium_risk_files', 'high_risk_files'];
            risks.forEach(risk => {
            if (dt[risk] && dt[risk].length > 0) {
                reportHTML += `<h4>${risk.replace('_', ' ').toUpperCase()}</h4><ul>`;
                dt[risk].forEach(item => {
                reportHTML += `<li><strong>File:</strong> ${item.file}<br>`;
                reportHTML += `<strong>File Hash:</strong> ${item.file_hash}<br>`;
                reportHTML += `<strong>Bandit Report:</strong><ul>`;
                item.bandit_report.forEach(report => {
                    reportHTML += `<li><strong>Issue:</strong> ${report.issue_text}<br>`;
                    reportHTML += `<strong>Severity:</strong> ${report.issue_severity}<br>`;
                    reportHTML += `<strong>Confidence:</strong> ${report.issue_confidence}<br>`;
                    reportHTML += `<strong>Line Number:</strong> ${report.line_number}<br>`;
                    reportHTML += `<strong>Code:</strong> <pre>${report.code}</pre></li>`;
                });
                reportHTML += `</ul></li>`;
                });
                reportHTML += `</ul>`;

            } else {
                reportHTML += `<h4>${risk.replace('_', ' ').toUpperCase()}</h4><p>No files found</p>`;
            }
            });
        });

        reportHTML += `</div>
                </div>`;

        feedbackPanel.innerHTML = reportHTML;
    }


