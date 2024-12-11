{pkgs}: {
  deps = [
    pkgs.libffi
    pkgs.gdk-pixbuf
    pkgs.cairo
    pkgs.pango
    pkgs.harfbuzz
    pkgs.glib
    pkgs.ghostscript
    pkgs.fontconfig
    pkgs.openssl
    pkgs.postgresql
  ];
}
