%if 0%{?this_is_intentionally_unterminated}
Name: broken-spec-package
Version: 1.0
Release: 1%{?dist}
Summary: A spec with an unterminated conditional, to exercise the exclude-resolver's fallback branch

License: GPLv3+

%description
This spec is intentionally unparseable by rpmspec (missing %endif) so that
resolve_exclude_packages.yml's "spec exists but failed to parse" fallback
branch has real functional test coverage instead of only ad-hoc manual checks.

%files
