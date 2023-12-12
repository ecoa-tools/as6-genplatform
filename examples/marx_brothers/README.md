# Marx Example

## Purpose

This is an ECOA example which calls every ECOA API to test syntax,
availability and warning generation.

It is not aimed to check if the behaviour fulfill the whole standard
requirements.


## Covered APIs

APIs below are mainly used through the C binding

| API                     | Component(s)    | C | C++ |
|-------------------------|-----------------|---|-----|
| request\_received       | cadet, junior   | X |     |
| response\_received      | cadet           | X |     |
| updated                 | cadet           | X |     |
| event received          | all             | X | X   |
| lifecycle               | all             | X | X   |
| response\_send          | cadet, junior   | X |     |
| request\_sync           | elder           | X |     |
| request\_async          | cadet           | X |     |
| read access             | *elder, cadet*  | X |     |
| write access            | *cadet*, junior | X |     |
| event send              | all             | X |     |
| property                | elder           | X |     |
| Log                     | all             | X |     |
| Raise                   | elder           | X |     |
| Time                    | elder           | X |     |
| Pinfo read              | elder           | X |     |
| Pinfo seek              | elder           | X |     |
| External Interface      | junior          | X | X   |
| Periodic Trigger        | elder           | X |     |
| Dynamic Trigger         | *junior*        | X |     |
| C++ module              | junior          |   | X   |


## APIs not covered

- fault handler
- save_warm_start
- recovery_action

