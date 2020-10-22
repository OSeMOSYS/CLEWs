""" Creates the SETS, FUELS and COMMODITIES in MoManI for the energy sector and the land use (from clustered AEZ data).

This script (C) Taco Niet 2019

"""
def BuildCLEWsModel(data):
    import sys
    import os

    import colorama

    from Create_Energy_Set import create_set
    from Fill_Empty_Sets import Fill_Set
    from Create_Energy_Set import AddActivityListItems

    colorama.init()
    import decimal

    # create a decimal context
    ctx = decimal.Context()
    # Set to 4 Sig Figs for MoManI speed
    ctx.prec = 2
    # Unpacking variables
    Model = data['Model']
    OutputFormat = data['OutputFormat']
    otooleOutputDirectory = data['otooleOutputDirectory']
    Years = [str(i) for i in data['Years']]
    Emissions = data['Emissions']
    Timeslices = data['Timeslices']
    Regions = data['Regions']
    EndUseFuels = data['EndUseFuels']
    PowerPlants = data['PowerPlants']
    LandToGridMap = data['LandToGridMap']
    TransformationTechnologies = data['TransformationTechnologies']
    ImportFuels = data['ImportFuels']
    DomesticMining = data['DomesticMining']
    DomesticRenewables = data['DomesticRenewables']
    ExportFuels = data['ExportFuels']
    LandRegions = data['LandRegions']
    DataDirectoryName = data['DataDirectoryName']
    ClusterBaseFileName = data['ClusterBaseFileName']
    PrecipitationClusterBaseFileName = data['PrecipitationClusterBaseFileName']
    EvapotranspirationClusterBaseFileName = data['EvapotranspirationClusterBaseFileName']
    IrrigationWaterDeficitClusterBaseFileName = data['IrrigationWaterDeficitClusterBaseFileName']
    IrrigationTypeList = data['IrrigationTypeList']
    IntensityList = data['IntensityList']
    CropYieldFactors = data['CropYieldFactors']
    GroundwaterPercentofExcess = data['GroundwaterPercentofExcess']
    LandUseCodes = data['LandUseCodes']
    EvapotranspirationPercentPRCOtherLandUse = data['EvapotranspirationPercentPRCOtherLandUse']
    GroundwaterPercentofExcessOtherLandUse = data['GroundwaterPercentofExcessOtherLandUse']


    # ***************************** #
    # CREATE ENERGY SET INFORMATION #
    # ***************************** #

    # Create empty list for new sets
    SetNames = []
    NewSetItems = []
    NewSetGroups = []
    IARList = []
    OARList = []



    # Create set YEARS
    # First create the new set name for year and add space for groups and items for this set
    create_set(SetNames, NewSetItems, NewSetGroups, 'YEAR')
    for year in Years:
        # Cannot use the same function as other sets as YEAR does not have a 'name' field and this crashes MoManI...
        NewSetItems[SetNames.index('YEAR')].append({'value': year, 'color': '#000000'})
       
    # Create set EMISSIONS
    # First create the new set name for year and add space for groups and items for this set
    create_set(SetNames, NewSetItems, NewSetGroups, 'EMISSION')
    for emission in Emissions:
        Fill_Set(NewSetItems, SetNames, "EMISSION", emission, Emissions[emission][1], Emissions[emission][0])

    # Create set TIMESLICE
    # First create the new set name for year and add space for groups and items for this set
    create_set(SetNames, NewSetItems, NewSetGroups, 'TIMESLICE')
    for timeslice in Timeslices:
        Fill_Set(NewSetItems, SetNames, "TIMESLICE", timeslice, Timeslices[timeslice][1], Timeslices[timeslice][0])

    # Create set REGION
    # First create the new set name for year and add space for groups and items for this set
    create_set(SetNames, NewSetItems, NewSetGroups, 'REGION')
    for Region in Regions:
        Fill_Set(NewSetItems, SetNames, "REGION", Region, Regions[Region][1], Regions[Region][0])

    # Create empty set TECHNOLOGY
    create_set(SetNames, NewSetItems, NewSetGroups, 'TECHNOLOGY')

    # Create empty set COMMODITY
    create_set(SetNames, NewSetItems, NewSetGroups, 'COMMODITY')


    # Create sectoral demand technologies
    for sector in EndUseFuels:
        for fuel in EndUseFuels[sector]:
            # Create the demand fuel:
            Fill_Set(NewSetItems, SetNames, "COMMODITY", sector + fuel, "#000000", "")
            # Create the demand technology
            Fill_Set(NewSetItems, SetNames, "TECHNOLOGY", "DEM" + sector + fuel, "#000000", "Demand technology for ")
            # Create the input fuel (if it doesn't exist)
            if not fuel in [li['value'] for li in NewSetItems[SetNames.index("COMMODITY")]]:
                Fill_Set(NewSetItems, SetNames, "COMMODITY", fuel, "#000000", "")

            # Create the input and output activity for that combination:
            AddActivityListItems(Years, Region, "DEM" + sector + fuel, sector + fuel, OARList, value = "1")
            AddActivityListItems(Years, Region, "DEM" + sector + fuel, fuel, IARList, value = "1")


    for powerplant in PowerPlants:
        if not powerplant[3:6] in [li['value'] for li in NewSetItems[SetNames.index("COMMODITY")]]:
            Fill_Set(NewSetItems, SetNames, "COMMODITY", powerplant[3:6], "#000000", "")
        if not "PWR" + powerplant[3:6] in [li['value'] for li in NewSetItems[SetNames.index("COMMODITY")]]:
            Fill_Set(NewSetItems, SetNames, "COMMODITY", "PWR" + powerplant[3:6], "#000000", "")

            AddActivityListItems(Years, Region, "DEMPWR" + powerplant[3:6], powerplant[3:6], IARList, value = "1")
            AddActivityListItems(Years, Region, "DEMPWR" + powerplant[3:6], "PWR" + powerplant[3:6], OARList, value = "1")
        if not "DEMPWR" + powerplant[3:6] in [li['value'] for li in NewSetItems[SetNames.index("TECHNOLOGY")]]:
            Fill_Set(NewSetItems, SetNames, "TECHNOLOGY", "DEMPWR" + powerplant[3:6], "#000000", "")

        # Create ELC001 commodity if not already created.  But do this per land region (using the first character of the last three digits of the power plant as the key):
        if not "ELC" + powerplant[6:7] + "01" in [li['value'] for li in NewSetItems[SetNames.index("COMMODITY")]]:
            Fill_Set(NewSetItems, SetNames, "COMMODITY", "ELC" + powerplant[6:7] + "01", "#000000", "")
        Fill_Set(NewSetItems, SetNames, "TECHNOLOGY", powerplant, "#000000", PowerPlants[powerplant][0])

        AddActivityListItems(Years, Region, powerplant, "PWR" + powerplant[3:6], IARList, value = str(PowerPlants[powerplant][1]),
                v = str(PowerPlants[powerplant][1]))
        AddActivityListItems(Years, Region, powerplant, "ELC" + powerplant[6:7] + "01", OARList, value = "1")

        # Create input surface water.

        LandRegion = [k for k, v in LandToGridMap.items() if v == powerplant[6:7]][0]
        if not "DEMPWRSUR" + LandRegion in [li['value'] for li in NewSetItems[SetNames.index("TECHNOLOGY")]]:
            Fill_Set(NewSetItems, SetNames, "TECHNOLOGY","DEMPWRSUR" + LandRegion,
            "#000000",  "", "Surface water demand for power in " + LandRegion)
        if not "PWRWAT" + LandRegion in [li['value'] for li in NewSetItems[SetNames.index("COMMODITY")]]:
            Fill_Set(NewSetItems, SetNames, "COMMODITY","PWRWAT" + LandRegion,
            "#000000",  "", "Surface water demand for power in " + LandRegion)

            AddActivityListItems(Years, Region, "DEMPWRSUR" + LandRegion, "WTRSUR" + LandRegion, IARList, value = "1")
            AddActivityListItems(Years, Region, "DEMPWRSUR" + LandRegion, "PWRWAT" + LandRegion, OARList, value = "1")


        AddActivityListItems(Years, Region, powerplant, "PWRWAT" + LandRegion, IARList, value = str(PowerPlants[powerplant][2]),
                v = str(PowerPlants[powerplant][2]))
        AddActivityListItems(Years, Region, powerplant, "WTRSUR" + LandRegion, OARList, value = str(PowerPlants[powerplant][3]),
                v = str(PowerPlants[powerplant][3]))


    for transformationtech in TransformationTechnologies:
        if not transformationtech[0] in [li['value'] for li in NewSetItems[SetNames.index("TECHNOLOGY")]]:
            NewSetItems[SetNames.index("TECHNOLOGY")].append(
                {"value": transformationtech[0], "name": transformationtech[5], "color": "#000000"})

        if transformationtech[1] != '':
            AddActivityListItems(Years, Region, transformationtech[0], transformationtech[1], IARList, value = str(transformationtech[2]),
                g = transformationtech[6], v = str(transformationtech[2]))

        if transformationtech[3] != '':
            AddActivityListItems(Years, Region, transformationtech[0], transformationtech[3], OARList, value = str(transformationtech[4]),
                g = transformationtech[6], v = str(transformationtech[4]))



    # Create import fuels
    for fuel in ImportFuels:
        if not fuel in [li['value'] for li in NewSetItems[SetNames.index("COMMODITY")]]:
            print("")
            print("\x1b[0;30;41mWarning:  Import fuel " + fuel + " created for fuel that is not used in any sector.\x1b[0m")
            print("")
            Fill_Set(NewSetItems, SetNames, "COMMODITY", fuel, "#000000",  "")
        Fill_Set(NewSetItems, SetNames, "TECHNOLOGY", "IMP" + fuel, "#000000",  "")
        AddActivityListItems(Years, Region, "IMP" + fuel, fuel, OARList, value = "1")

    # Create domestic supply of fuels
    for fuel in DomesticMining:
        if not fuel in [li['value'] for li in NewSetItems[SetNames.index("COMMODITY")]]:
            print("")
            print(
                "\x1b[0;30;41mWarning:  Mining of fuel " + fuel + " created for fuel that is not used in any sector.\x1b[0m")
            print("")
            Fill_Set(NewSetItems, SetNames, "COMMODITY", fuel, "#000000",  "")
        Fill_Set(NewSetItems, SetNames, "TECHNOLOGY", "MIN" + fuel, "#000000",  "")
        AddActivityListItems(Years, Region, "MIN" + fuel, fuel, OARList, value = "1")

    # Create domestic supply of renewables
    for fuel in DomesticRenewables:
        if not fuel in [li['value'] for li in NewSetItems[SetNames.index("COMMODITY")]]:
            print("")
            print(
                "\x1b[0;30;41mWarning:  Renewable fuel " + fuel + " created for fuel that is not used in any sector.\x1b[0m")
            print("")
            Fill_Set(NewSetItems, SetNames, "COMMODITY", fuel, "#000000",  "")
        Fill_Set(NewSetItems, SetNames, "TECHNOLOGY", "RNW" + fuel, "#000000",  "")
        AddActivityListItems(Years, Region, "RNW" + fuel, fuel, OARList, value = "1")

    # Create export fuels
    for fuel in ExportFuels:
        if not fuel in [li['value'] for li in NewSetItems[SetNames.index("COMMODITY")]]:
            print("")
            print(
                "\x1b[0;30;41mWarning:  Export fuel " + fuel + " created for fuel that is not used/produced in any sector.\x1b[0m")
            print("")
            Fill_Set(NewSetItems, SetNames, "COMMODITY", fuel, "#000000",  "")
        Fill_Set(NewSetItems, SetNames, "TECHNOLOGY", "EXP" + fuel, "#000000",  "")
        AddActivityListItems(Years, Region, "EXP" + fuel, fuel, IARList, value = "1")


    # ******************************************** #
    # AGRICULTURAL TECHNOLOGIES, FUELS AND IAR/OAR #
    # ******************************************** #

    # Create groups for sets to track commodities, technologies
    # Don't need groups for these for agriculture - can add later if needed...
    # Make all set colour black for the time being - can change later if needed...

    CropList = {}
    CropNumber = 1
    CropComboList = {}
    ModeList = []
    ModeNumber = 1

    for LandRegion in LandRegions:
        ###############################
        # Inputs for agricultural groundwater and electricity for pumping:
        Fill_Set(NewSetItems, SetNames, "TECHNOLOGY", "DEMAGRGWT" + LandRegion, "#000000", "Agricultural groundwater supply.")
        Fill_Set(NewSetItems, SetNames, "TECHNOLOGY", "DEMAGRSUR" + LandRegion, "#000000", "Agricultural groundwater supply.")
        Fill_Set(NewSetItems, SetNames, "COMMODITY", "AGRWAT" + LandRegion, "#000000", "Agricultural water for irrigation.")
        Fill_Set(NewSetItems, SetNames, "COMMODITY", "WTREVT" + LandRegion, "#000000", "Water lost to evapotranspiration.")
        Fill_Set(NewSetItems, SetNames, "COMMODITY", "WTRGRC" + LandRegion, "#000000", "Water lost to evapotranspiration.")
        Fill_Set(NewSetItems, SetNames, "TECHNOLOGY", "DEMPUBGWT" + LandRegion, "#000000", "Agricultural water for irrigation.")
        Fill_Set(NewSetItems, SetNames, "TECHNOLOGY", "DEMPUBSUR" + LandRegion, "#000000", "Agricultural water for irrigation.")
        Fill_Set(NewSetItems, SetNames, "COMMODITY", "PUBWAT" + LandRegion, "#000000", "Water lost to evapotranspiration.")

        # Creation of agricultural water supply from grownwater
        # 1.73 number taken from Bolivia - Should be 0.0173
        # NEED TO ADJUST THE IAR TO MATCH THE CORRECT VALUE FOR THE DEMAGRGWT...
        AddActivityListItems(Years, Region, "DEMAGRGWT" + LandRegion, "AGRELC" + LandToGridMap[LandRegion] + "02", IARList, value = "0.0173",
                v = "0.0173")

        # for year in Years:
        # Sets = [Region, "DEMAGRGWT"+LandRegion, "WTRGWT"+LandRegion, "1", year]
        # Value = "1"
        # Item = {"c":Sets, "v":Value}
        # IARList.append(Item)
        AddActivityListItems(Years, Region, "DEMAGRGWT" + LandRegion, "AGRWAT" + LandRegion, OARList, value = "1")

        # Creation of agricultural water supply from surface water
        # for year in Years:
        # Sets = [Region, "DEMAGRSUR"+LandRegion, "AGRELC"+LandToGridMap[LandRegion], "1", year]
        # Value = "0.0173"
        # # 1.73 number taken from Bolivia
        # # NEED TO ADJUST THE IAR TO MATCH THE CORRECT VALUE FOR THE DEMAGRGWT...
        # Item = {"c":Sets, "v":Value}
        # IARList.append(Item)
        AddActivityListItems(Years, Region, "DEMAGRSUR" + LandRegion, "WTRSUR" + LandRegion, IARList, value = "1")
        AddActivityListItems(Years, Region, "DEMAGRSUR" + LandRegion, "AGRWAT" + LandRegion, OARList, value = "1")


        # Creation of public water supply from surface water
        # for year in Years:
        # Sets = [Region, "DEMPUBSUR"+LandRegion, "COMELC"+LandToGridMap[LandRegion], "1", year]
        # Value = "0.0173"
        # # 1.73 number taken from Bolivia
        # # NEED TO ADJUST THE IAR TO MATCH THE CORRECT VALUE FOR THE DEMAGRGWT...
        # Item = {"c":Sets, "v":Value}
        # IARList.append(Item)
        AddActivityListItems(Years, Region, "DEMPUBSUR" + LandRegion, "WTRSUR" + LandRegion, IARList, value = "1")
        AddActivityListItems(Years, Region, "DEMPUBSUR" + LandRegion, "PUBWAT" + LandRegion, OARList, value = "1")

        # Creation of public water supply from groundwater water
        # 1.73 number taken from Bolivia
        # NEED TO ADJUST THE IAR TO MATCH THE CORRECT VALUE FOR THE DEMAGRGWT...
        AddActivityListItems(Years, Region, "DEMPUBGWT" + LandRegion, "COMELC" + LandToGridMap[LandRegion] + "02", IARList, value = "0.0173",
                v = "0.0173")

        # for year in Years:
        # Sets = [Region, "DEMPUBGWT"+LandRegion, "WTRGWT"+LandRegion, "1", year]
        # Value = "1"
        # Item = {"c":Sets, "v":Value}
        # IARList.append(Item)
        AddActivityListItems(Years, Region, "DEMPUBGWT" + LandRegion, "PUBWAT" + LandRegion, OARList, value = "1")


        ###############################
        # Precipitation sources
        Fill_Set(NewSetItems, SetNames, "TECHNOLOGY", "MINPRC" + LandRegion, "#000000", "Agricultural groundwater supply.")
        Fill_Set(NewSetItems, SetNames, "COMMODITY", "WTRPRC" + LandRegion, "#000000", "Agricultural water for irrigation.")
        AddActivityListItems(Years, Region, "MINPRC" + LandRegion, "WTRPRC" + LandRegion, OARList, value = "1")

        ###############################
        # Groundwater sources
        # NewSetItems[SetNames.index("TECHNOLOGY")].append({"value":"MINGWT"+LandRegion, "name":"Agricultural groundwater supply.", "color":"#000000"})
        # NewSetItems[SetNames.index("COMMODITY")].append({"value":"WTRGWT"+LandRegion, "name":"Agricultural water for irrigation.", "color":"#000000"})
        # for year in Years:
        # Sets = [Region, "MINGWT"+LandRegion, "WTRGWT"+LandRegion, "1", year]
        # Value = "1"
        # Item = {"c":Sets, "v":Value}
        # OARList.append(Item)    ###############################
        # Surfce water sources
        #    NewSetItems[SetNames.index("TECHNOLOGY")].append({"value":"MINSUR"+LandRegion, "name":"Agricultural groundwater supply.", "color":"#000000"})
        Fill_Set(NewSetItems, SetNames, "COMMODITY", "WTRSUR" + LandRegion, "#000000", "Agricultural water for irrigation.")
        #    for year in Years:
        #        Sets = [Region, "MINSUR"+LandRegion, "WTRSUR"+LandRegion, "1", year]
        #        Value = "1"
        #        Item = {"c":Sets, "v":Value}
        #        OARList.append(Item)    ###############################
        # Land resource
        Fill_Set(NewSetItems, SetNames, "TECHNOLOGY", "MINLND" + LandRegion, "#000000", "Land suuply in ")
        Fill_Set(NewSetItems, SetNames, "COMMODITY", "L" + LandRegion, "#000000", "Land resource in " + LandRegion + ".")
        AddActivityListItems(Years, Region, "MINLND" + LandRegion, "L" + LandRegion, OARList, value = "1")

        ###############################
        # Cluster specific technologies for different crops, etc...
        Clusters = open(os.path.join(DataDirectoryName, ClusterBaseFileName + LandRegion + '.csv'), 'r').readlines()
        PrecipitationClusters = open(os.path.join(DataDirectoryName, PrecipitationClusterBaseFileName + LandRegion + '.csv'),
                                     'r').readlines()
        EvapotranspirationClusters = open(os.path.join(DataDirectoryName, EvapotranspirationClusterBaseFileName + LandRegion + '.csv'),
                                          'r').readlines()
        IrrigationWaterDeficitClusters = open(
            os.path.join(DataDirectoryName, IrrigationWaterDeficitClusterBaseFileName + LandRegion + '.csv'), 'r').readlines()
        # Create list of crops (or add crops to list), intensities, technology
        for Combo in Clusters[0].split(",")[10:]:
            Crop = ' '.join(Combo.split(' ')[:-2])
            IrrigationType = Combo.split(' ')[-2][0]
            Intensity = Combo.split(' ')[-1][0]
            # We have a crop combination.  We need to check if we have the crop already, and if not add a new crop.
            if Crop in CropList:  # We have already dealt with this crop in another situation...
                CropCode = CropList[Crop]
            else:
                CropCode = "CP" + str(CropNumber).zfill(2)
                CropNumber = CropNumber + 1
                CropList[Crop] = CropCode
                # And create the crop commodity for final output:
                Fill_Set(NewSetItems, SetNames, "COMMODITY", "CRP" + CropCode, "#000000", Crop)
            # And then we need to check if we have the combination already, and if not add it to the list.
            if CropCode + Intensity + IrrigationType in CropComboList:
                CropCombo = CropComboList[CropCode + Intensity + IrrigationType]
            else:
                # We don't have this one yet:
                CropCombo = CropCode + Intensity + IrrigationType
                CropComboList[CropCode + Intensity + IrrigationType] = CropCombo
                ModeList.append(CropCombo)
                ModeNumber = ModeNumber + 1
            # This crop combo might exist in other regions, but we need to add it to this region...
            Fill_Set(NewSetItems, SetNames, "TECHNOLOGY", "LND" + CropCombo + LandRegion, "#000000",
            "Land resource technology for crop combo " + Combo)
            Fill_Set(NewSetItems, SetNames, "COMMODITY", "L" + CropCombo + LandRegion, "#000000",
            "Land resource commodity for crop combo " + Combo)
            AddActivityListItems(Years, Region, "LND" + CropCombo + LandRegion, "L" + LandRegion, IARList, value = "1")
            AddActivityListItems(Years, Region, "LND" + CropCombo + LandRegion, "L" + CropCombo + LandRegion, OARList, value = "1")

        # Crops and land tracking commodities have been created.  Now create land technologies to connect them together.
        for clustercount in range(1, len(Clusters)):
            # Add the agricultural land use technologies
            Fill_Set(NewSetItems, SetNames, "TECHNOLOGY", "LNDAGR" + LandRegion + "C" + Clusters[clustercount].split(',')[0].zfill(2),
            "#000000","Land resource in " + LandRegion + ".")
            # And add a mode for each crop combination and create the IAR and OAR
            for mode, modeCombo in enumerate(ModeList):
                # Add the IAR for the combo into the correct mode.
                AddActivityListItems(Years, Region, "LNDAGR" + LandRegion + "C" + Clusters[clustercount].split(',')[0].zfill(2),
                "L" + modeCombo + LandRegion, IARList, value = "1",  g = str(mode + 1))

                # And add the OAR for the output crop:
                # Lookup the OAR from the cluster data:
                for CropCode2, cropcombo2 in CropList.items():
                    if modeCombo[:-2] == cropcombo2:
                        # IAR for Precipitation - Should only be entered if the combination exists
                        PrecipitationValue = float(PrecipitationClusters[clustercount].split(',')[
                                                       1])  # Precipitation values are constant across all technologies/crops in a region.
                        PrecipitationValue = format(ctx.create_decimal(repr(PrecipitationValue)), 'f')

                        AddActivityListItems(Years, Region,
                        "LNDAGR" + LandRegion + "C" + PrecipitationClusters[clustercount].split(',')[0].zfill(2),
                        "WTRPRC" + LandRegion, IARList, g = str(mode + 1), v = str(PrecipitationValue))

                        # Find the right OAR for this technology and put it into the OAR list:

                        CropComboLabel = CropCode2 + " " + IrrigationTypeList[modeCombo[-1]] + " " + IntensityList[
                            modeCombo[-2]]
                        Location = Clusters[0].strip().split(',').index(CropComboLabel)
                        Value = float(Clusters[clustercount].split(',')[Location]) * CropYieldFactors[CropComboLabel[0:4]]
                        Value = format(ctx.create_decimal(repr(Value)), 'f')

                        AddActivityListItems(Years, Region,
                        "LNDAGR" + LandRegion + "C" + Clusters[clustercount].split(',')[0].zfill(2),
                        "CRP" + modeCombo[:-2], OARList, g = str(mode + 1), v = str(Value))

                        # IAR for Irrigation
                        Location = IrrigationWaterDeficitClusters[0].strip().split(',').index(CropComboLabel)
                        IrrigationValue = float(IrrigationWaterDeficitClusters[clustercount].split(',')[Location])
                        if IrrigationTypeList[modeCombo[-1]] == 'Rain-fed':
                            IrrigationValue = 0.
                        IrrigationValue = format(ctx.create_decimal(repr(IrrigationValue)), 'f')
                        if float(
                                IrrigationValue) < 0.0001:  # fix to prevent scientific e-8 numbers from breaking the system.
                            IrrigationValue = '0'

                        AddActivityListItems(Years, Region,
                        "LNDAGR" + LandRegion + "C" + IrrigationWaterDeficitClusters[clustercount].split(',')[0].zfill(2),
                        "AGRWAT" + LandRegion, IARList, g = str(mode + 1), v = str(IrrigationValue))

                        # OAR for Evapotranspiration
                        Location = EvapotranspirationClusters[0].strip().split(',').index(CropComboLabel)
                        EvapotranspirationValue = float(EvapotranspirationClusters[clustercount].split(',')[Location])
                        EvapotranspirationValue = format(ctx.create_decimal(repr(EvapotranspirationValue)), 'f')
                        # print(CropComboLabel+" "+line.split(',')[0] + " " + Value)
                        # print(str(mode)+" "+modeCombo+ " "+CropCode2+ " "+cropcombo2)

                        AddActivityListItems(Years, Region,
                        "LNDAGR" + LandRegion + "C" + EvapotranspirationClusters[clustercount].split(',')[0].zfill(2),
                        "WTREVT" + LandRegion, OARList, g = str(mode + 1), v = str(EvapotranspirationValue))

                        # OAR for Groundwater
                        GroundwaterValue = (float(PrecipitationValue) + float(IrrigationValue) - float(
                            EvapotranspirationValue)) * GroundwaterPercentofExcess
                        GroundwaterValue = format(ctx.create_decimal(repr(GroundwaterValue)), 'f')
                        RunoffValue = (float(PrecipitationValue) + float(IrrigationValue) - float(
                            EvapotranspirationValue)) * (1 - GroundwaterPercentofExcess)
                        RunoffValue = format(ctx.create_decimal(repr(RunoffValue)), 'f')

                        AddActivityListItems(Years, Region,
                        "LNDAGR" + LandRegion + "C" + EvapotranspirationClusters[clustercount].split(',')[0].zfill(2),
                        "WTRGRC" + LandRegion, OARList, g = str(mode + 1), v = str(GroundwaterValue))

                        # OAR for Runoff
                        AddActivityListItems(Years, Region,
                        "LNDAGR" + LandRegion + "C" + EvapotranspirationClusters[clustercount].split(',')[0].zfill(2),
                        "WTRSUR" + LandRegion, OARList, g = str(mode + 1), v = str(RunoffValue))

        # ADD LAST FEW MODES, AND IAR FOR THEM IN LNDAGR technologies
        for LandUseCode, LandUse in LandUseCodes.items():
            if LandUse in ModeList:
                ModeNum = ModeList.index(LandUse)
                # Mode exists, use this one...
                # print(str(ModeNum)+LandUse+ModeList[ModeNum])
            else:
                # Mode doesn't exist, create new mode.
                ModeList.append(LandUse)
                ModeNum = ModeNumber - 1
                ModeNumber = ModeNumber + 1
                # print(str(ModeNum)+LandUse+ModeList[ModeNum])
            # print(str(ModeNum)+LandUse+ModeList[ModeNum])
            # Now add the land use sets, IAR and OAR to connect to the LNDAGR technologies...
            Fill_Set(NewSetItems, SetNames, "TECHNOLOGY", "LND" + LandUseCode + LandRegion, "#000000",
            LandUse + " technology in " + LandRegion + ".")
            Fill_Set(NewSetItems, SetNames, "COMMODITY", "L" + LandUseCode + LandRegion, "#000000",
            LandUse + " commodity in " + LandRegion + ".")

            # LSOU becomes LNDFORSOU, etc. in mode 1
            AddActivityListItems(Years, Region, "LND" + LandUseCode + LandRegion, "L" + LandRegion, IARList, value = "1")

            # LNDFORSOU becomes LFORSOU, etc. in mode 1
            AddActivityListItems(Years, Region, "LND" + LandUseCode + LandRegion, "L" + LandUseCode + LandRegion, OARList, value = "1")

            for line in Clusters[1:]:  # Have to have the output for all lines...
                # LSOU becomes LNDFORSOU, etc. in specified mode
                AddActivityListItems(Years, Region, "LNDAGR" + LandRegion + "C" + line.split(',')[0].zfill(2),
                "L" + LandUseCode + LandRegion, IARList, value = "1", g = str(ModeNum + 1)) # print(Sets)


                # Now add precipitation and water balance inputs and outputs
                PrecipitationValue = float(PrecipitationClusters[int(line.split(',')[0])].split(',')[
                                               1])  # Precipitation values are constant across all technologies/crops in a region.
                PrecipitationValue = format(ctx.create_decimal(repr(PrecipitationValue)), 'f')

                AddActivityListItems(Years, Region,
                        "LNDAGR" + LandRegion + "C" + line.split(',')[0].zfill(2),
                        "WTRPRC" + LandRegion, IARList, g = str(ModeNum + 1), v = str(PrecipitationValue))



                # IAR for Irrigation doesn't exist - there is no irrigation for these technologies as they are not agricultural.
                # OAR for Evapotranspiration
                EvapotranspirationValue = float(PrecipitationValue) * EvapotranspirationPercentPRCOtherLandUse[LandUseCode]
                EvapotranspirationValue = format(ctx.create_decimal(repr(EvapotranspirationValue)), 'f')
                # print(CropComboLabel+" "+line.split(',')[0] + " " + Value)
                # print(str(mode)+" "+modeCombo+ " "+CropCode2+ " "+cropcombo2)

                AddActivityListItems(Years, Region,
                        "LNDAGR" + LandRegion + "C" + line.split(',')[0].zfill(2),
                        "WTREVT" + LandRegion, OARList, g = str(ModeNum + 1), v = str(EvapotranspirationValue))

                # OAR for Groundwater
                GroundwaterValue = (float(PrecipitationValue) - float(EvapotranspirationValue)) * \
                                   GroundwaterPercentofExcessOtherLandUse[LandUseCode]
                GroundwaterValue = format(ctx.create_decimal(repr(GroundwaterValue)), 'f')
                RunoffValue = (float(PrecipitationValue) - float(EvapotranspirationValue)) * (
                            1 - GroundwaterPercentofExcessOtherLandUse[LandUseCode])
                RunoffValue = format(ctx.create_decimal(repr(RunoffValue)), 'f')

                AddActivityListItems(Years, Region,
                        "LNDAGR" + LandRegion + "C" + line.split(',')[0].zfill(2),
                        "WTRGRC" + LandRegion, OARList, g = str(ModeNum + 1), v = str(GroundwaterValue))

                # OAR for Runoff
                AddActivityListItems(Years, Region,
                        "LNDAGR" + LandRegion + "C" + line.split(',')[0].zfill(2),
                        "WTRSUR" + LandRegion, OARList, g = str(ModeNum + 1), v = str(RunoffValue))


    # ************************* #
    # CREATE MODES OF OPERATION #
    # ************************* #

    SetNames.append("MODE_OF_OPERATION")
    NewSetItems.append([])
    NewSetGroups.append([])
    for index, Mode in enumerate(ModeList):
        Fill_Set(NewSetItems, SetNames, "MODE_OF_OPERATION", str(index + 1), "#000000", Mode)

    with open('ModeList.txt', 'w') as ModeFile:
        ModeFile.write(str(ModeList))

    # ******************************* #
    # Remove any 0's from IAR and OAR #
    # ******************************* #

    for i, dic in enumerate(IARList):
        if float(dic['v']) == float('0'):
            IARList.pop(i)

    for i, dic in enumerate(OARList):
        if float(dic['v']) == float('0'):
            OARList.pop(i)

    if OutputFormat == 'MoManI':
        # *************************** #
        # UPDATE MOMANI WITH NEW DATA #
        # *************************** #
        from UpdateMoManI import UpdateMoManI
        UpdateMoManI(Model, SetNames, NewSetItems, NewSetGroups, IARList, OARList)

    if OutputFormat == 'otoole':
        # *************************** #
        # output to otoole format     #
        # *************************** #
        from Updateotoole import Updateotoole
        Updateotoole(SetNames, NewSetItems, IARList, OARList, otooleOutputDirectory)


def main():
    import argparse, yaml
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Location of YAML file that describes the CLEWs model structure.")
    args = parser.parse_args()
    if args.file:
        with open(args.file, "r") as file_descriptor:
            data = yaml.safe_load(file_descriptor)
        BuildCLEWsModel(data)

if __name__ == "__main__":
   main()