-- PRX silo extensions: adds the fill types in prx_fillTypes.xml that the game, the map or another mod hasn't
-- already defined, then builds the PRXSILO category the storages use. Existing types are never touched.

local modDirectory = g_currentModDirectory
local modName = g_currentModName

local function loadPRXFillTypes(manager)
    local xmlFile = XMLFile.load("prxFillTypes", modDirectory .. "prx_fillTypes.xml", FillTypeManager.xmlSchema)
    if xmlFile == nil then
        Logging.error("PRX: could not load prx_fillTypes.xml")
        return
    end

    local numAdded = 0
    for _, key in xmlFile:iterator("map.fillTypes.fillType") do
        local name = xmlFile:getValue(key .. "#name")
        if name ~= nil and manager:getFillTypeByName(name) == nil then
            local fillTypeDesc = FillTypeDesc.new()
            if fillTypeDesc:loadFromXMLFile(xmlFile, key, modDirectory, modName) and manager:addFillType(fillTypeDesc) then
                fillTypeDesc:finalize()
                numAdded = numAdded + 1
            end
        end
    end

    for _, key in xmlFile:iterator("map.fillTypeCategories.fillTypeCategory") do
        local categoryIndex = manager:addFillTypeCategory(xmlFile:getValue(key .. "#name"), false)
        local fillTypeNames = xmlFile:getValue(key)
        if categoryIndex ~= nil and fillTypeNames ~= nil then
            for _, fillTypeName in ipairs(fillTypeNames) do
                local fillType = manager:getFillTypeByName(fillTypeName)
                if fillType ~= nil then
                    manager:addFillTypeToCategory(fillType.index, categoryIndex)
                end
            end
        end
    end

    xmlFile:delete()
    Logging.info("PRX: added %d fill types that weren't already in the game", numAdded)
end

FillTypeManager.loadMapData = Utils.appendedFunction(FillTypeManager.loadMapData, function(self, xmlFile, missionInfo, baseDirectory)
    loadPRXFillTypes(self)
end)
