async function load() {
    try {
        let currentUrl = window.location.href;
        currentUrl = currentUrl.split('/').slice(0, -2).join('/');

        const package_ecosystem = document.getElementById("ecosystem").value;

        switch (package_ecosystem) {
            case "crates.io":
            currentUrl = currentUrl + '/get_rust_packages';
            break;
            case "wolfi":
            currentUrl = currentUrl + '/get_wolfi_packages';
            break;
            case "npm":
            currentUrl = currentUrl + '/get_npm_packages';
            break;
            case "pypi":
            currentUrl = currentUrl + '/get_pypi_packages';
            break;
            case "rubygems":
            currentUrl = currentUrl + '/get_rubygems_packages';
            break;
            case "maven":
            currentUrl = currentUrl + '/get_maven_packages';
            break;
            case "packagist":
            currentUrl = currentUrl + '/get_packagist_packages';
            break;
            default:
            throw new Error("Unsupported ecosystem selected");
        }

        let response = await fetch(currentUrl);
        let data = await response.json();
        return data;
    } catch (error) {
        console.error('Error:', error);
        return [];
    }
}

async function get_pypi_versions(package_name) {
    try {
        let currentUrl = window.location.href;
        currentUrl = currentUrl.split('/').slice(0, -2).join('/');
        currentUrl = currentUrl + '/get_pypi_versions?package_name=' + encodeURIComponent(package_name);
        let response = await fetch(currentUrl);
        let data = await response.json();
        return data;
    } catch (error) { 
        console.error('Error:', error);
        return [];
    }
}

// Function to get the package versions for npm packages
async function get_npm_versions(package_name) {
    try {
        let currentUrl = window.location.href;
        currentUrl = currentUrl.split('/').slice(0, -2).join('/');
        currentUrl = currentUrl + '/get_npm_versions?package_name=' + encodeURIComponent(package_name);
        let response = await fetch(currentUrl);
        let data = await response.json();
        return data;
    } catch (error) { 
        console.error('Error:', error);
        return [];
    }
}

// Function to get the package versions for packagist packages
async function get_packagist_versions(package_name) {
    try {
        let currentUrl = window.location.href;
        currentUrl = currentUrl.split('/').slice(0, -2).join('/');
        currentUrl = currentUrl + '/get_packagist_versions?package_name=' + encodeURIComponent(package_name);
        let response = await fetch(currentUrl);
        let data = await response.json();
        return data;
    } catch (error) { 
        console.error('Error:', error);
        return [];
    }
}

// Function to get the package versions for rubygems packages
async function get_rubygems_versions(package_name) {
    try {
        let currentUrl = window.location.href;
        currentUrl = currentUrl.split('/').slice(0, -2).join('/');
        currentUrl = currentUrl + '/get_rubygems_versions?package_name=' + encodeURIComponent(package_name);
        let response = await fetch(currentUrl);
        let data = await response.json();
        return data;
    } catch (error) { 
        console.error('Error:', error);
        return [];
    }
}



/*
document.addEventListener("DOMContentLoaded", () => { 

    // display only the first 100 package_version in the select box
    const packageVersion = document.getElementById("package_version");
    const packageVersionOptions = Array.from(packageVersion.options);
    const maxOptions = 100; // Maximum number of options to display
    const limitedOptions = packageVersionOptions
                            .sort((a, b) => a.text.localeCompare(b.text))
                            .slice(0, maxOptions);
    packageVersion.innerHTML = ""; 
    limitedOptions.forEach(option => {
        packageVersion.appendChild(option);
    });
    packageVersion.style.display = "block"; 

});

*/


// document.addEventListener("DOMContentLoaded", () => {
//     const input = document.getElementById("package_name");
//     const packageVersion = document.getElementById("package_version");
//     const ecosystem = document.getElementById("ecosystem");
//     const suggestions = document.getElementById("suggestions");

//     const loadPackages = () => {
//         load().then(packages => {
//             input.addEventListener("input", function() {
//                 const value = this.value.toLowerCase();
//                 suggestions.innerHTML = "";

//                 let package_names = [];
//                 if (ecosystem.value === "crates.io") {
//                     package_names = Object.keys(packages);
//                 } else if (ecosystem.value === "pypi") {
//                     package_names = packages.packages;
//                 } else if (ecosystem.value === "npm") {
//                     package_names = packages.packages;
//                 } else if (ecosystem.value === "packagist") {
//                     package_names = packages.packages;
//                 } else if (ecosystem.value === "rubygems") {
//                     package_names = packages.packages;
//                 }

//                 if (value) {
//                     const filteredPackages = package_names
//                         .filter(package_name => package_name.toLowerCase().startsWith(value))
//                         .sort((a, b) => a.localeCompare(b))
//                         .slice(0, 1000);

//                     if (filteredPackages.length > 0) {
//                         suggestions.style.display = "block";
//                         filteredPackages.forEach(package_name => {
//                             const div = document.createElement("div");
//                             div.textContent = package_name;
//                             div.addEventListener("click", async function() {
//                                 input.value = package_name;
//                                 suggestions.style.display = "none";

//                                 let versions = [];
//                                 if (ecosystem.value === "crates.io") {
//                                     versions = packages[package_name].slice().reverse();
//                                 } else if (ecosystem.value === "pypi") {
//                                     const pypiData = await get_pypi_versions(package_name);
//                                     versions = pypiData.versions.slice().reverse();
//                                 } else if (ecosystem.value === "npm") {
//                                     const npmData = await get_npm_versions(package_name);
//                                     versions = npmData.versions.slice().reverse();
//                                 } else if (ecosystem.value === "packagist") {
//                                     const packagistData = await get_packagist_versions(package_name);
//                                     versions = packagistData.versions.slice();
//                                 } else if (ecosystem.value === "rubygems") {
//                                     const rubygemsData = await get_rubygems_versions(package_name);
//                                     versions = rubygemsData.versions.slice();
//                                 }


//                                 packageVersion.innerHTML = ""; // Clear previous options
//                                 packageVersion.style.display = "block"; // Show the select box
//                                 packageVersion.removeAttribute("disabled"); // Enable the select box
//                                 if (versions.length > 0) {
//                                     versions.forEach(version => {
//                                         const option = document.createElement("option");
//                                         option.value = version;
//                                         option.textContent = version;
//                                         packageVersion.appendChild(option);
//                                     });
//                                 } else {
//                                     packageVersion.style.display = "none";
//                                 }
//                             });
//                             suggestions.appendChild(div);
//                         });
//                     } else {
//                         suggestions.style.display = "none";
//                     }
//                 } else {
//                     suggestions.style.display = "none";
//                 }
//             });
//         });
//     };

//     // Load packages initially
//     loadPackages();

//     // Reload packages when ecosystem changes
//     ecosystem.addEventListener("change", () => {
//         input.value = ""; // Clear the input field
//         suggestions.innerHTML = ""; // Clear suggestions
//         packageVersion.innerHTML = ""; // Clear package versions
//         packageVersion.style.display = "none"; // Hide the select box
//         loadPackages(); // Reload packages
//     });

//     document.addEventListener("click", (e) => {
//         if (!document.querySelector("#package_name").contains(e.target) && !suggestions.contains(e.target)) {
//             suggestions.style.display = "none";
//         }
//     });
// });


document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("package_name");
    const ecosystem = document.getElementById("ecosystem");
    const suggestions = document.getElementById("suggestions");
    const versionSuggestions = document.getElementById("version-suggestions");
    const packageVersion = document.getElementById("package_version");

    const loadPackages = () => {
        load().then(packages => {
            input.addEventListener("input", function () {
                const value = this.value.toLowerCase();
                suggestions.innerHTML = "";
                versionSuggestions.innerHTML = ""; // Clear previous version suggestions

                let package_names = [];
                if (ecosystem.value === "crates.io") {
                    package_names = Object.keys(packages);
                } else if (["pypi", "npm", "packagist", "rubygems"].includes(ecosystem.value)) {
                    package_names = packages.packages;    
                } else if (ecosystem.value === "maven") {
                    // packages_names will list GroupId:ArtifactId
                    //   exxampel of data "groupID: {"artifactID": ["version1", "version2"]}

                    package_names = Object.keys(packages).map(groupId => {
                        return Object.keys(packages[groupId]).map(artifactId => {
                            return `${groupId}:${artifactId}`;
                        });
                    }).flat();
                } else if (ecosystem.value === "wolfi") {
                    package_names = packages.packages.packages;
                }

                if (value) {
                    const filteredPackages = package_names
                        .filter(package_name => package_name.toLowerCase().startsWith(value))
                        .sort((a, b) => a.localeCompare(b))
                        .slice(0, 1000);

                    if (filteredPackages.length > 0) {
                        suggestions.style.display = "block";
                        filteredPackages.forEach(package_name => {
                            const div = document.createElement("div");
                            div.textContent = package_name;
                            div.addEventListener("click", async function () {
                                input.value = package_name;
                                suggestions.style.display = "none";

                                let versions = [];
                                if (ecosystem.value === "crates.io") {
                                    versions = packages[package_name].slice().reverse();
                                } else if (ecosystem.value === "pypi") {
                                    const pypiData = await get_pypi_versions(package_name);
                                    versions = pypiData.versions.slice().reverse();
                                } else if (ecosystem.value === "npm") {
                                    const npmData = await get_npm_versions(package_name);
                                    versions = npmData.versions.slice().reverse();
                                } else if (ecosystem.value === "packagist") {
                                    const packagistData = await get_packagist_versions(package_name);
                                    versions = packagistData.versions.slice();
                                } else if (ecosystem.value === "rubygems") {
                                    const rubygemsData = await get_rubygems_versions(package_name);
                                    versions = rubygemsData.versions.slice();
                                } else if (ecosystem.value === "maven") {
                                    const [groupId, artifactId] = package_name.split(":");
                                    if (packages[groupId] && packages[groupId][artifactId]) {
                                        versions = packages[groupId][artifactId].slice().reverse();
                                    } 
                                } else if (ecosystem.value === "wolfi") {
                                    //version will be the package name
                                    versions = [package_name];
                                }
                                
                                versionSuggestions.innerHTML = ""; // Clear previous suggestions
                                if (versions.length > 0) {
                                    versionSuggestions.style.display = "block"; // Show version suggestions
                                    versions.forEach(version => {
                                        const versionDiv = document.createElement("div");
                                        versionDiv.textContent = version;
                                        versionDiv.addEventListener("click", function () {
                                            packageVersion.value = version; // Set the selected version in the input form
                                            versionSuggestions.style.display = "none"; // Hide version suggestions
                                        });
                                        versionSuggestions.appendChild(versionDiv);
                                    });
                                } else {
                                    const noVersionsDiv = document.createElement("div");
                                    noVersionsDiv.textContent = "No versions available";
                                    noVersionsDiv.classList.add("no-versions");
                                    versionSuggestions.appendChild(noVersionsDiv);
                                    packageVersion.value = "latest";
                                }
                            });
                            suggestions.appendChild(div);
                        });
                    } else {
                        suggestions.style.display = "none";
                    }
                } else {
                    suggestions.style.display = "none";
                }
            });
        });
    };

    // Load packages initially
    loadPackages();

    // Reload packages when ecosystem changes
    ecosystem.addEventListener("change", () => {
        input.value = ""; // Clear the input field
        suggestions.innerHTML = ""; // Clear suggestions
        versionSuggestions.innerHTML = ""; // Clear version suggestions
        versionSuggestions.value = ""; // Clear selected version
        loadPackages(); // Reload packages
    });

    document.addEventListener("click", (e) => {
        if (!document.querySelector("#package_name").contains(e.target) && !suggestions.contains(e.target)) {
            suggestions.style.display = "none";
        }
    });
});