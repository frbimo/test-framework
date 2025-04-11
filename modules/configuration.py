import re
from pydantic import (
    BaseModel, Field, AnyUrl, model_validator, field_validator,
    ValidationError
)
from typing import List, Optional, Union, Dict, Any
from enum import Enum

# --- Re-define necessary Enums (with added docstrings) ---

class DeploymentArchitectureEnum(str, Enum):
    """Specifies the general physical environment for the deployment."""
    INDOOR = "indoor"
    OUTDOOR = "outdoor"

class DeploymentScaleEnum(str, Enum):
    """Specifies the scale or cell size of the deployment."""
    MICRO = "micro"
    PICO = "pico"
    MACRO = "macro"

class DeploymentRfScenarioEnum(str, Enum):
    """Describes the radio frequency propagation environment."""
    RURAL = "rural"
    URBAN = "urban"
    DENSE_URBAN = "dense.urban"
    LOS = "LOS"  # Line of Sight
    NLOS = "NLOS" # Non Line of Sight
    NLOS_ALT = "nLOS" # Non Line of Sight (alternative notation)

class FrequencyRange5GEnum(str, Enum):
    """Indicates the 5G NR frequency range (FR1: sub-6GHz, FR2: mmWave)."""
    FR1 = "fr1"
    FR2_1 = "fr2-1" # mmWave sub-range 1
    FR2_2 = "fr2-2" # mmWave sub-range 2
    FR2_NTN = "fr2-ntn" # mmWave for Non-Terrestrial Networks

# (Add docstrings similarly to other Enums like Band5GEnum, BandLTEEnum, etc. if needed)
class Band5GEnum(str, Enum):
    """Specific 5G NR operating band number (e.g., n78)."""
    N1 = "n1"; N2 = "n2"; N3 = "n3"; N5 = "n5"; N7 = "n7"; N8 = "n8"
    N12 = "n12"; N13 = "n13"; N14 = "n14"; N18 = "n18"; N20 = "n20"
    N24 = "n24"; N25 = "n25"; N26 = "n26"; N28 = "n28"; N29 = "n29"
    N30 = "n30"; N31 = "n31"; N34 = "n34"; N38 = "n38"; N39 = "n39"
    N40 = "n40"; N41 = "n41"; N46 = "n46"; N48 = "n48"; N50 = "n50"
    N51 = "n51"; N53 = "n53"; N54 = "n54"; N65 = "n65"; N66 = "n66"
    N70 = "n70"; N71 = "n71"; N72 = "n72"; N74 = "n74"; N75 = "n75"
    N76 = "n76"; N77 = "n77"; N78 = "n78"; N79 = "n79"; N80 = "n80"
    N81 = "n81"; N82 = "n82"; N83 = "n83"; N84 = "n84"; N85 = "n85"
    N86 = "n86"; N89 = "n89"; N90 = "n90"; N91 = "n91"; N92 = "n92"
    N93 = "n93"; N94 = "n94"; N95 = "n95"; N96 = "n96"; N97 = "n97"
    N98 = "n98"; N99 = "n99"; N100 = "n100"; N101 = "n101"; N102 = "n102"
    N103 = "n103"; N104 = "n104"; N105 = "n105"; N106 = "n106"; N109 = "n109"
    N254 = "n254"; N255 = "n255"; N256 = "n256"; N257 = "n257"; N258 = "n258"
    N259 = "n259"; N260 = "n260"; N261 = "n261"; N262 = "n262"; N263 = "n263"
    N510 = "n510"; N511 = "n511"; N512 = "n512"


class BandLTEEnum(str, Enum):
    """Specific LTE E-UTRA operating band number (e.g., 41)."""
    B1="1"; B2="2"; B3="3"; B4="4"; B5="5"; B6="6"; B7="7"; B8="8"; B9="9"
    B10="10"; B11="11"; B12="12"; B13="13"; B14="14"; B16="16"; B17="17"
    B18="18"; B19="19"; B20="20"; B21="21"; B22="22"; B23="23"; B24="24"
    B25="25"; B26="26"; B27="27"; B28="28"; B29="29"; B30="30"; B31="31"
    B32="32"; B33="33"; B34="34"; B35="35"; B36="36"; B37="37"; B38="38"
    B39="39"; B40="40"; B41="41"; B42="42"; B43="43"; B44="44"; B45="45"
    B46="46"; B47="47"; B48="48"; B49="49"; B50="50"; B51="51"; B52="52"
    B53="53"; B54="54"; B55="55"; B56="56"; B57="57"; B58="58"; B59="59"
    B60="60"; B61="61"; B62="62"; B63="63"; B64="64"; B65="65"; B66="66"
    B67="67"; B68="68"; B69="69"; B70="70"; B71="71"; B72="72"; B73="73"
    B74="74"; B75="75"; B76="76"; B85="85"; B87="87"; B88="88"; B103="103"
    B106="106"; B107="107"; B108="108"


class SubCarrierSpacingEnum(str, Enum):
    """The subcarrier spacing (SCS) used in the OFDM waveform (kHz)."""
    KHZ_15 = "15kHz"
    KHZ_30 = "30kHz"
    KHZ_60 = "60kHz"

class DuplexModeEnum(str, Enum):
    """The duplexing scheme used (Time Division Duplex or Frequency Division Duplex)."""
    TDD = "tdd"
    FDD = "fdd"


# --- Enhanced ConfigurationParameters Class ---

class ConfigurationParameters(BaseModel):
    """
    Holds various configuration parameters applied during O-RAN testing.
    This can include deployment details, RF settings, network configuration,
    and antenna properties. It allows for both standard parameters defined
    here and potentially vendor-specific additional parameters.
    """
    deploymentArchitecture: Optional[DeploymentArchitectureEnum] = Field(
        None,
        description="Specifies the general physical environment for the deployment (e.g., indoor, outdoor)."
    )
    deploymentScale: Optional[DeploymentScaleEnum] = Field(
        None,
        description="Specifies the scale or cell size of the deployment (e.g., micro, pico, macro)."
    )
    deploymentRfScenario: Optional[DeploymentRfScenarioEnum] = Field(
        None,
        description="Describes the radio frequency propagation environment (e.g., rural, urban, LOS, NLOS)."
    )
    frequencyRange5G: Optional[List[FrequencyRange5GEnum]] = Field(
        None,
        min_length=1,
        description="List of 5G NR frequency ranges (FR1, FR2) used during the test."
    )
    band5G: Optional[List[Band5GEnum]] = Field(
        None,
        min_length=1,
        description="List of specific 5G NR operating band numbers (e.g., n78, n257) used."
    )
    bandLTE: Optional[List[BandLTEEnum]] = Field(
        None,
        min_length=1,
        description="List of specific LTE E-UTRA operating band numbers (e.g., 3, 41) used, if applicable."
    )
    nr_arfcn: Optional[float] = Field(
        None,
        alias="nr-arfcn",
        ge=0,
        description="NR Absolute Radio Frequency Channel Number used for the carrier."
    )
    e_arfcn: Optional[float] = Field(
        None,
        alias="e-arfcn",
        ge=0,
        description="E-UTRA Absolute Radio Frequency Channel Number used for the carrier, if applicable."
    )
    subCarrierSpacing: Optional[SubCarrierSpacingEnum] = Field(
        None,
        description="The subcarrier spacing (SCS) in kHz used in the OFDM waveform (e.g., 15kHz, 30kHz)."
    )
    totalTransmissionBandwidth: Optional[float] = Field(
        None,
        ge=0,
        description="The total transmission bandwidth configured, typically in MHz."
    )
    totalResourceBlocks: Optional[int] = Field(
        None,
        ge=0,
        description="The total number of Physical Resource Blocks (PRBs) configured for the carrier bandwidth."
    )
    carrierPrefixLength: Optional[int] = Field(
        None,
        description="Length of the carrier prefix (e.g., for specific synchronization or channel configurations)."
    )
    slotLength: Optional[int] = Field(
        None,
        description="Duration of a slot, often in microseconds or related to OFDM symbols."
    )
    duplexMode: Optional[DuplexModeEnum] = Field(
        None,
        description="The duplexing scheme used (TDD or FDD)."
    )
    # # This is the correct TIFG spec. For PoC on integration with RICTEST tddDlUlRatio should value string like 7:3
    # tddDlUlRatio: Optional[float] = Field(
    #     None,
    #     description="For TDD mode, the ratio or pattern describing Downlink (DL) vs Uplink (UL) transmission time."
    # )

    tddDlUlRatio: Optional[str] = Field(
        None,
        description="For TDD mode, the ratio or pattern describing Downlink (DL) vs Uplink (UL) transmission time."
    )
    ipv4: Optional[bool] = Field(
        None,
        description="Indicates if IPv4 networking was enabled or primarily used for relevant interfaces."
    )
    ipv6: Optional[bool] = Field(
        None,
        description="Indicates if IPv6 networking was enabled or primarily used for relevant interfaces."
    )
    numMimoLayers: Optional[int] = Field(
        None,
        ge=0,
        description="Number of MIMO (Multiple-Input Multiple-Output) spatial layers configured or achieved."
    )
    numTxAntenna: Optional[int] = Field(
        None,
        ge=0,
        description="Number of physical transmit antenna elements used by the component."
    )
    numRxAntenna: Optional[int] = Field(
        None,
        ge=0,
        description="Number of physical receive antenna elements used by the component."
    )
    totalAntennaGain: Optional[float] = Field(
        None,
        description="Total gain of the antenna system, typically in dBi."
    )
    totalTransmitPowerIntoAntenna: Optional[float] = Field(
        None,
        description="Total power transmitted into the antenna element(s), often measured in dBm or Watts."
    )

    # Custom settings or vendor-specific parameters  (RICTEST)
    numberOfCells: Optional[int] = Field(
        None,
        description="Number of cells configured in the test setup."
    )
    azimuth: Optional[int] = Field(
        None,
    )
    tilt: Optional[int] = Field(
        None,
    )
    height: Optional[int] = Field(
        None,
    )
    # Allow additional properties as defined in schema
    # The class docstring already mentions this possibility.

    @model_validator(mode='before')
    @classmethod
    def check_min_properties(cls, data: Any) -> Any:
        if isinstance(data, dict) and not data:
             raise ValueError("ConfigurationParameters must have at least one property.")
        return data

    model_config = {
        'populate_by_name': True, # Allows using aliases like 'nr-arfcn'
        'extra': 'allow'          # Allow fields not explicitly defined above
    }

# Example of how you might use this class definition with an LLM (conceptual)

hypothetical_vendor_text = """
Test Setup Configuration:
- Deployment: Outdoor Macro Cell
- RF Environment: Urban NLOS
- Frequency: 5G NR FR1, Band n78
- Channel Bandwidth: 100 MHz
- SCS: 30 kHz
- ARFCN: 633334
- Duplex: TDD, pattern DDDSU (represents roughly 3:1 DL/UL ratio)
- Antennas: 4T4R configuration
- Tx Power per port: 37 dBm
- Custom Setting Alpha: Enabled
- Network: IPv4 only
"""
