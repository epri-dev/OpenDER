
Changelog
=========
Unreleased changes
------------------
* Updated volt-var curve point setting and nameplate information validity check
* Fixed a minor bug for PV DER, watt-var function
* Fixed a bug/typo in frequency-droop function

2.1.5 (2024-06-12)
------------------
* Fixed a FutureWarning for pandas version 2.2.
* Fixed bugs for single phase model.
* Fixed a bug for negative sequence performance for Momentary Cessation

2.1.4 (2024-03-29)
------------------
* Added a setting to enable and disable momentary cessation (MC_ENABLE)
* Added settings to configure the momentary cessation voltage threshold (MC_LVRT_V1, MC_HVRT_V1)
* Fixed a bug on momentary cessation not triggering on high voltage condition.
* If NP_PHASE is set to 1 or 3, it will be automatically converted to 'SINGLE' or 'THREE'

2.1.3 (2023-12-05)
------------------
* Added a property for SoC of BESS DER using .bess_soc
* Automatically update the reactive capability curve if nameplate parameter is modified
  (when user defined curve is not provided)

2.1.2 (2023-08-23)
------------------
* Fixed an issue for BESS parameter initialization

2.1.1 (2023-08-18)
------------------
* Fixed an issue on voltage source output when zero sequence voltage is present
* Corrected single phase DER voltage measurement

2.1.0 (2023-05-29)
------------------
* Updated interaction between enter service ramp and ride-through. Now DER returns to enter service ramp
  after ride-through
* Added an optional charge/discharge ramp rate limit for BESS DER
* Added resets for all grid-support functions when DER is tripped

2.0.3 (2023-04-14)
------------------
* Fixed the option to update BESS DER parameter when creating the object.
* Fixed a bug when initializing a BESS DER during abnormal frequency condition.

2.0.2 (2023-04-03)
------------------
* Fixed a bug abnormal operation category (NP_ABNORMAL_OP_CAT) only accepts uppercase values
* Updated ride-through performance to better represent actual inverter's behavior
* Added an option to update DER parameter when creating the object.

2.0.1 (2023-03-21)
------------------
* Fixed a bug where enter service randomized enter delay does not behave as expected
* Fixed a bug where momentary cessation does not behave as expected

2.0.0 (2023-03-20)
------------------
* Changed all units of nameplate rating to the base unit Watt/var/VA, from kW/kvar/kVA in Version 1.0.
* Added one time delay feature to represent the DER active and reactive grid support functions’ reaction time, and a first order lag for in applicable voltage measurement.
* Added Battery Energy Storage System (BESS) DER specific functions including State-of-Charge (SOC) calculation, and their corresponding model input parameters.
* Updated applicable smart inverter functions to consider BESS DER behaviors, including volt-watt, active power limit, and watt-var functions.
* Changed the DER operation status from ON/OFF to “Continuous Operation”, “Mandatory Operation”, “Momentary Cessation”, “Trip”, etc., to better capture the DER ride-through status, and its performance in different ride-through modes.
* Added DER ride-through performance module, which includes the DER performance under different ride-through modes, including Momentary Cessation, etc.
* Added DER model output options as current source and voltage source behind impedance.


1.0.2 (2022-07-18)
------------------
* Improve model input validity check process

1.0.1 (2022-06-17)
------------------
* Include parameter csv files into the PyPI release

1.0.0 (2022-05-17)
------------------
* First release
* Model for photovoltaic (PV) DERs, including all smart inverter functions defined in IEEE Standard 1547-2018, as well as trip and enter service behaviors
* Output active and reactive power (P, Q) for power flow analysis
* Suitable for both steady-state, quasi-static time series (QSTS) and dynamic simulations
