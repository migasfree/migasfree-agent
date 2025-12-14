#!/bin/bash
set -e

PROJECT_ROOT=$(pwd)
VERSION=${1:-"1.0.0"}
DEB_DIR="packaging/deb"
RPM_DIR="packaging/rpm"
DIST_DIR="dist"

echo "Building version $VERSION..."
mkdir -p $DIST_DIR

# Update Debian Control File Version
sed -i "s/^Version: .*/Version: $VERSION/" $DEB_DIR/DEBIAN/control

# --- BUILD DEB ---
echo "--- Building DEB Package ---"
# Copy files to structure
cp agent/migasfree-agent $DEB_DIR/usr/bin/migasfree-agent
chmod 755 $DEB_DIR/usr/bin/migasfree-agent

# Build
dpkg-deb --build $DEB_DIR $DIST_DIR

# --- BUILD RPM ---
echo "--- Building RPM Package ---"
# Check if rpmbuild exists
if command -v rpmbuild >/dev/null 2>&1; then
    # Create structure
    mkdir -p $RPM_DIR/{SOURCES,BUILD,RPMS,SRPMS}

    # Copy sources
    cp agent/migasfree-agent $RPM_DIR/SOURCES/migasfree-agent
    cp $DEB_DIR/lib/systemd/system/migasfree-agent.service $RPM_DIR/SOURCES/

    # Build
    rpmbuild --define "_topdir $PROJECT_ROOT/$RPM_DIR" --define "version $VERSION" -bb $RPM_DIR/SPECS/migasfree-agent.spec
    
    # Copy to dist
    cp $RPM_DIR/RPMS/noarch/*.rpm $DIST_DIR/
else
    echo "rpmbuild not found. Skipping RPM build."
fi

echo "✅ Build complete. Packages in $DIST_DIR/"
ls -l $DIST_DIR/
