---
title: Version Naming Rules
description: Introduction to ClickMouse version naming rules.
layout: doc
---

# Version Naming Rules
clickmouse version format is: `A.B.C.D[(alpha | beta |.dev | rc) E]`
## Official Versions
Official versions do not have .dev, alpha, beta, or rc suffixes.

A position represents major updates with code-level changes. For example, upgrading from 1.0 to 2.0 involves code refactoring.

B position represents regular updates, usually updating some major features.

C position represents fix updates, usually updating some small features and fixing some bugs.

D position represents version code, usually increments by 1 when A, B, C positions change. It is also possible that A, B, C positions do not change but D position increments by 1, representing emergency updates, usually fixing several major impact bugs.

## Test Versions
Test versions have .dev, alpha, beta, or rc suffixes.

Usually the preceding `A.B.C.D` does not change within a testing cycle, representing the next version.

`.dev` represents early development updates, features are unstable, many bugs, located in the early stage of version project.The new features in this phase will be put in the lab and turned off by default.

`alpha` represents late development updates, features are incomplete, many bugs, located in the early stage of version project.The new features in this phase will be put in the lab and turned off by default.

`beta` represents release testing updates, features are complete, few bugs, no new features will be added, located in the middle stage of version project. It is usually released in the middle of the development cycle and will gradually merge features from the lab.

`rc` represents release candidate versions, features are complete, few bugs, will fix some important security issues or bugs, closest to official version, about to release official version, located in the late stage of version project.

::: tip Tip
The last rc version will be directly merged into the beta version; features are exactly the same.
:::