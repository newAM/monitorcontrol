# This is a flake for use with NixOS
# See: https://nixos.wiki/wiki/Flakes
{
  description = "Monitor controls using MCCS over DDC-CI";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachSystem [ "x86_64-linux" "aarch64-linux" ] (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pyproject = nixpkgs.lib.importTOML ./pyproject.toml;
      in
      rec {
        packages.default = pkgs.python3.pkgs.buildPythonPackage rec {
          pname = pyproject.tool.poetry.name;
          inherit (pyproject.tool.poetry) version;
          format = "pyproject";

          src = ./.;

          nativeBuildInputs = [
            pkgs.python3.pkgs.poetry-core
          ];

          propagatedBuildInputs = [
            pkgs.python3.pkgs.pyudev
          ];

          checkInputs = [
            pkgs.python3.pkgs.pytestCheckHook
            pkgs.python3.pkgs.voluptuous
          ];

          pythonImportsCheck = [
            pname
          ];

          postInstall = ''
            mkdir -p $out/etc/udev/rules.d
            echo 'KERNEL=="i2c-[0-9]*", GROUP="i2c"' > $out/etc/udev/rules.d/10-i2c.rules
          '';

          meta = with nixpkgs.lib; {
            inherit (pyproject.tool.poetry) description;
            homepage = pyproject.tool.poetry.repository;
            license = with licenses; [ mit ];
          };
        };
        apps.default = flake-utils.lib.mkApp { drv = packages.default; };
        devShells.default = packages.default;

        checks = {
          format = pkgs.runCommand "format" { } ''
            ${pkgs.nixpkgs-fmt}/bin/nixpkgs-fmt --check ${./.}
            touch $out
          '';

          lint = pkgs.runCommand "lint" { } ''
            ${pkgs.statix}/bin/statix check ${./.}
            touch $out
          '';
        };
      }
    );
}
