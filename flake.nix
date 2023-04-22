# This is a flake for use with NixOS
# See: https://nixos.wiki/wiki/Flakes
{
  description = "Monitor controls using MCCS over DDC-CI";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  outputs = {
    self,
    nixpkgs,
  }: let
    pyproject = nixpkgs.lib.importTOML ./pyproject.toml;
    pname = pyproject.tool.poetry.name;

    python3Overlay = final: prev:
      prev.buildPythonPackage {
        inherit pname;
        inherit (pyproject.tool.poetry) version;
        format = "pyproject";

        src = builtins.path {
          path = ./.;
          name = "monitorcontrol";
        };

        nativeBuildInputs = [
          prev.poetry-core
        ];

        propagatedBuildInputs = [
          prev.pyudev
        ];

        checkInputs = [
          prev.pytestCheckHook
          prev.voluptuous
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
          license = with licenses; [mit];
        };
      };

    overlay = final: prev: rec {
      python3 = prev.python3.override {
        packageOverrides = final: prev: {
          monitorcontrol = python3Overlay final prev;
        };
      };
      python3Packages = python3.pkgs;
    };

    pkgs = import nixpkgs {
      system = "x86_64-linux";
      overlays = [overlay];
    };
  in {
    packages.x86_64-linux.default = pkgs.python3Packages.monitorcontrol;
    devShells.x86_64-linux.default = self.packages.x86_64-linux.default;

    formatter.x86_64-linux = nixpkgs.legacyPackages.x86_64-linux.alejandra;

    checks.x86_64-linux = {
      pkg = self.packages.x86_64-linux.default;

      alejandra = pkgs.runCommand "alejandra" {} ''
        ${pkgs.alejandra}/bin/alejandra --check ${./.}
        touch $out
      '';

      statix = pkgs.runCommand "statix" {} ''
        ${pkgs.statix}/bin/statix check ${./.}
        touch $out
      '';
    };
    overlays = {
      default = overlay;
      python3 = python3Overlay;
    };
  };
}
