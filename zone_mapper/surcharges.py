
# config for free and surcharge zips

freeZips = (
    # SF, eminating from ferry building
    94111,
    94105,
    94133,
    94108,
    94104,
    94109,
    94102,
    94103,
    #94158, # not in tiger data
    94123,
    94115,
    94117,
    94114,
    94110,
    94107,
    94129,
    94118,
    94131,
    94127,
    94112,
    94134,
    94124,
    94121,
    94122,
    94116,
    94132,
    94130, # treasure island

    # east bay, starting in north working south
    94805,
    94804,
    94530,
    94706,
    94707,
    94708,
    94710,
    94702,
    94703,
    94709,
    #94720, # not in tiger data
    94704,
    94705,
    94608,
    94609,
    94618,
    94611,
    94516,
    94607,
    94606,
    #94615, # not in tiger data
    94612,
    94610,
    94602,
    94619,
    94501,
    94601,
    #94613, # not in tiger data
    94605,
    94502,
    94621,
    94603,
    94577,
    94578,
    94579,
    94580,
)

surchargeZips = (
    # pennisula, working southward
    94015,
    94014,
    94005,
    94080,
    94044,
    94066,
    94128,
    94030,
    94010,
    94401,
    94402,
    94403,
    94404,
    94002,

    # east bay, from the south, working northward
    94545,
    94544,
    94542,
    94541,
    94552,
    94546,
    94568,
    94583,
    #94582, # not in tiger data
    94556,
    94526,
    94506,
    94549,
    94597,
    94595,
    94596,
    94507,
    94598,
    #94517, # clayton, goes far out east
    94520,
    94523,
    94518,
    94553,
    94569,
    94525,
    94572,
    94547,
    94564,
    94803,
    94806,
    94801,

    # orinda
    94563,

    # marin, south to north
    94965,
    94941,
    94920,
    94925,
    94939,
    94964,
    94904,
    94930,
    94960,
    94901,
    94903,
    94949,
)

def getFreeZips():
    return freeZips

def getSurchargeZips():
    return surchargeZips

def getDeliveryZips():
    return freeZips + surchargeZips

