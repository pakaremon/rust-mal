async function load() {
    try {
        let currentUrl = window.location.href;
        currentUrl = currentUrl.split('/package-analysis')[0] + '/package-analysis';
        let response = await fetch( `${currentUrl}/get_rust_packages`);
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


document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("package_name");
    const packageVersion = document.getElementById("package_version");
    const suggestions = document.getElementById("suggestions");

    load().then(packages => {
        input.addEventListener("input", function() {
            const value = this.value.toLowerCase();
            suggestions.innerHTML = "";
            const package_names = Object.keys(packages);
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
                        div.addEventListener("click", function() {
                            input.value = package_name;
                            suggestions.style.display = "none";

                            const versions = packages[package_name].slice().reverse();
                            packageVersion.innerHTML = ""; // Clear previous options
                            packageVersion.style.display = "block"; // Show the select box
                            //enable the select box
                            packageVersion.removeAttribute("disabled");
                            if (versions.length > 0) {
                                versions.forEach(version => {
                                    const option = document.createElement("option");
                                    option.value = version;
                                    option.textContent = version;
                                    packageVersion.appendChild(option);
                                });
                            } else {
                                packageVersion.style.display = "none";
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

    document.addEventListener("click", (e) => {
        if (!document.querySelector("#package_name").contains(e.target) && !suggestions.contains(e.target)) {
            suggestions.style.display = "none";
        }
    });
});   

 


