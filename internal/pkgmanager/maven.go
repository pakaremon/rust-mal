package pkgmanager

import (
	"encoding/xml"
	"fmt"
	"net/http"
	"strings"

	"github.com/ossf/package-analysis/pkg/api/pkgecosystem"
)

type mavenMetadata struct {
	Versioning struct {
		Latest string `xml:"latest"`
	} `xml:"versioning"`
}

func getMavenLatest(pkg string) (string, error) {
	groupID, artifactID := parseMavenPackage(pkg)
	url := fmt.Sprintf("https://repo1.maven.org/maven2/%s/%s/maven-metadata.xml", strings.ReplaceAll(groupID, ".", "/"), artifactID)
	resp, err := http.Get(url)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	decoder := xml.NewDecoder(resp.Body)
	var metadata mavenMetadata
	err = decoder.Decode(&metadata)
	if err != nil {
		return "", err
	}

	return metadata.Versioning.Latest, nil
}

func getMavenArchiveURL(pkgName, version string) (string, error) {
	groupID, artifactID := parseMavenPackage(pkgName)
	jarURL := fmt.Sprintf("https://repo1.maven.org/maven2/%s/%s/%s/%s-%s.jar",
		strings.ReplaceAll(groupID, ".", "/"), artifactID, version, artifactID, version)
	return jarURL, nil
}

func getMavenArchiveFilename(pkgName, version, _ string) string {
	_, artifactID := parseMavenPackage(pkgName)
	return fmt.Sprintf("%s-%s.jar", artifactID, version)
}

func parseMavenPackage(pkg string) (string, string) {
	parts := strings.Split(pkg, ":")
	if len(parts) != 2 {
		return "", ""
	}
	return parts[0], parts[1]
}

var mavenPkgManager = PkgManager{
	ecosystem:       pkgecosystem.Maven,
	latestVersion:   getMavenLatest,
	archiveURL:      getMavenArchiveURL,
	archiveFilename: getMavenArchiveFilename,
}
