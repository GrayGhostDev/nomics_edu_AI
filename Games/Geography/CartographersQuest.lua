-- Cartographer's Quest Script
-- Place this in ServerScriptService

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

-- Create the main game module
local CartographersQuest = {}
CartographersQuest.__index = CartographersQuest

function CartographersQuest.new()
    local self = setmetatable({}, CartographersQuest)
    
    self.maps = {}
    self.playerData = {}
    self.tools = {}
    self.missions = {}
    
    -- Create remote events
    self.remotes = {
        CreateMap = Instance.new("RemoteEvent"),
        ExploreArea = Instance.new("RemoteEvent"),
        MapElevation = Instance.new("RemoteEvent"),
        MapResources = Instance.new("RemoteEvent"),
        OptimizeTradeRoute = Instance.new("RemoteEvent"),
        UpgradeTool = Instance.new("RemoteEvent"),
        CompleteMission = Instance.new("RemoteEvent")
    }
    
    for name, remote in pairs(self.remotes) do
        remote.Name = name
        remote.Parent = ReplicatedStorage
    end
    
    self:initializeTools()
    self:initializeMissions()
    self:setupEventHandlers()
    
    return self
end

-- Initialize tools
function CartographersQuest:initializeTools()
    self.tools = {
        compass = {
            name = "Navigation Compass",
            level = 1,
            accuracy = 0.85,
            upgradeCost = 50
        },
        ruler = {
            name = "Cartographer's Ruler",
            level = 1,
            precision = 0.90,
            upgradeCost = 60
        },
        protractor = {
            name = "Angle Protractor",
            level = 1,
            angleAccuracy = 0.88,
            upgradeCost = 55
        },
        theodolite = {
            name = "Digital Theodolite",
            level = 0,
            accuracy = 0.95,
            upgradeCost = 200,
            locked = true
        }
    }
end

-- Initialize missions
function CartographersQuest:initializeMissions()
    self.missions = {
        survey = {
            name = "Survey the Northern Region",
            description = "Map the terrain features of the northern region",
            reward = {gold = 100, experience = 50}
        },
        resource = {
            name = "Resource Mapping",
            description = "Identify and map natural resources",
            reward = {gold = 150, experience = 75}
        },
        expedition = {
            name = "Coastal Expedition",
            description = "Map the entire coastline",
            reward = {gold = 300, experience = 100}
        }
    }
end

-- Setup event handlers
function CartographersQuest:setupEventHandlers()
    self.remotes.CreateMap.OnServerEvent:Connect(function(player, mapName, terrainType)
        self:createMap(player, mapName, terrainType)
    end)
    
    self.remotes.ExploreArea.OnServerEvent:Connect(function(player, x, y, radius)
        self:exploreArea(player, x, y, radius)
    end)
    
    self.remotes.MapElevation.OnServerEvent:Connect(function(player, x, y)
        self:mapElevation(player, x, y)
    end)
    
    self.remotes.MapResources.OnServerEvent:Connect(function(player, x, y)
        self:mapResources(player, x, y)
    end)
    
    self.remotes.OptimizeTradeRoute.OnServerEvent:Connect(function(player, startPoint, endPoint)
        self:optimizeTradeRoute(player, startPoint, endPoint)
    end)
    
    self.remotes.UpgradeTool.OnServerEvent:Connect(function(player, toolName)
        self:upgradeTool(player, toolName)
    end)
    
    self.remotes.CompleteMission.OnServerEvent:Connect(function(player, missionType)
        self:completeMission(player, missionType)
    end)
    
    Players.PlayerAdded:Connect(function(player)
        self:initializePlayerData(player)
    end)
end

-- Initialize player data
function CartographersQuest:initializePlayerData(player)
    self.playerData[player.UserId] = {
        maps = {},
        currentMap = nil,
        cartographySkills = {
            accuracy = 1,
            detail = 1,
            interpretation = 1,
            topography = 1
        },
        tools = table.clone(self.tools),
        resources = {
            gold = 100,
            timber = 50,
            stone = 30,
            water = 100
        },
        completedMissions = {},
        experience = 0
    }
end

-- Create map
function CartographersQuest:createMap(player, mapName, terrainType)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    local map = {
        name = mapName,
        terrain = terrainType,
        features = {},
        resources = {},
        elevation = {},
        completed = false,
        accuracy = 0
    }
    
    -- Generate random features
    self:generateFeatures(map)
    
    playerData.maps[mapName] = map
    playerData.currentMap = map
    
    -- Create physical map representation
    self:createPhysicalMap(player, map)
    
    self.remotes.CreateMap:FireClient(player, {
        success = true,
        map = map
    })
end

-- Generate map features
function CartographersQuest:generateFeatures(map)
    local featuresByTerrain = {
        mountain = {"Peak", "Valley", "Ridge", "Pass"},
        coastal = {"Bay", "Peninsula", "Inlet", "Beach"},
        forest = {"Clearing", "River", "Lake", "Waterfall"},
        desert = {"Oasis", "Dune", "Canyon", "Mesa"}
    }
    
    local features = featuresByTerrain[map.terrain] or {}
    
    for i = 1, math.random(3, 6) do
        local feature = {
            type = features[math.random(#features)],
            x = math.random(100),
            y = math.random(100),
            discovered = false
        }
        table.insert(map.features, feature)
    end
end

-- Create physical map representation
function CartographersQuest:createPhysicalMap(player, map)
    -- Clear existing map
    for _, obj in ipairs(workspace:GetChildren()) do
        if obj:FindFirstChild("CartographerMap") then
            obj:Destroy()
        end
    end
    
    local mapModel = Instance.new("Model")
    mapModel.Name = map.name .. "_Map"
    
    local tag = Instance.new("BoolValue")
    tag.Name = "CartographerMap"
    tag.Parent = mapModel
    
    -- Create map table
    local mapTable = Instance.new("Part")
    mapTable.Name = "MapTable"
    mapTable.Size = Vector3.new(20, 1, 20)
    mapTable.Position = Vector3.new(0, 3, 0)
    mapTable.Anchored = true
    mapTable.BrickColor = BrickColor.new("Reddish brown")
    mapTable.Parent = mapModel
    
    -- Create map surface
    local mapSurface = Instance.new("Part")
    mapSurface.Name = "MapSurface"
    mapSurface.Size = Vector3.new(19, 0.1, 19)
    mapSurface.Position = Vector3.new(0, 3.6, 0)
    mapSurface.Anchored = true
    mapSurface.BrickColor = BrickColor.new("Parchment")
    mapSurface.Parent = mapModel
    
    mapModel.Parent = workspace
end

-- Explore area
function CartographersQuest:exploreArea(player, x, y, radius)
    local playerData = self.playerData[player.UserId]
    
    if not playerData or not playerData.currentMap then
        return
    end
    
    local map = playerData.currentMap
    local discovered = 0
    
    for _, feature in ipairs(map.features) do
        if not feature.discovered then
            local distance = math.sqrt((feature.x - x)^2 + (feature.y - y)^2)
            
            if distance <= radius then
                feature.discovered = true
                discovered = discovered + 1
            end
        end
    end
    
    if discovered > 0 then
        playerData.cartographySkills.accuracy = playerData.cartographySkills.accuracy + (discovered * 0.5)
        playerData.experience = playerData.experience + (discovered * 10)
        
        -- Update map accuracy
        map.accuracy = math.min(100, map.accuracy + (discovered * 5))
    end
    
    self.remotes.ExploreArea:FireClient(player, {
        success = true,
        discovered = discovered,
        mapAccuracy = map.accuracy
    })
end

-- Map elevation
function CartographersQuest:mapElevation(player, x, y)
    local playerData = self.playerData[player.UserId]
    
    if not playerData or not playerData.currentMap then
        return
    end
    
    local map = playerData.currentMap
    local elevation = 0
    
    -- Calculate elevation based on map features
    for _, feature in ipairs(map.features) do
        if feature.type == "Mountain" then
            elevation = elevation + 100
        elseif feature.type == "Valley" then
            elevation = elevation - 50
        end
    end

    playerData.elevation = elevation
    
    self.remotes.MapElevation:FireClient(player, {
        success = true,
        elevation = elevation
    })
end

-- Map resources
function CartographersQuest:mapResources(player, x, y)
    local playerData = self.playerData[player.UserId]
    
    if not playerData or not playerData.currentMap then
        return
    end
    
    local map = playerData.currentMap
    local resources = {}
    
    -- Generate random resources
    local resourceTypes = {"Timber", "Stone", "Water"}
    for _, resourceType in ipairs(resourceTypes) do
        local resourceAmount = math.random(1, 10)
        resources[resourceType] = resourceAmount
    end
    
    playerData.resources = resources
    
    self.remotes.MapResources:FireClient(player, {
        success = true,
        resources = resources
    })
end

-- Optimize trade route
function CartographersQuest:optimizeTradeRoute(player, startPoint, endPoint)
    local playerData = self.playerData[player.UserId]
    
    if not playerData or not playerData.currentMap then
        return
    end
    
    local map = playerData.currentMap
    local route = self:findOptimalRoute(map, startPoint, endPoint)
    
    if route then
        playerData.tradeRoutes[route.name] = route
    end
    
    self.remotes.OptimizeTradeRoute:FireClient(player, {
        success = true,
        route = route
    })
end

-- Complete mission
function CartographersQuest:completeMission(player, missionId)
    local playerData = self.playerData[player.UserId]
    
    if not playerData or not playerData.missions[missionId] then
        return
    end
    
    local mission = playerData.missions[missionId]
    
    -- Check if mission is completed
    if mission.isCompleted then
        playerData.experience = playerData.experience + mission.xpReward
        playerData.missions[missionId] = nil  -- Remove completed mission
        
        self.remotes.CompleteMission:FireClient(player, {
            success = true,
            xpReward = mission.xpReward,
            message = "Mission completed successfully!"
        })
    else
        self.remotes.CompleteMission:FireClient(player, {
            success = false,
            message = "Mission is not yet completed."
        })
    end
end

-- Find optimal route
function CartographersQuest:findOptimalRoute(map, startPoint, endPoint)
    -- Placeholder for route finding logic
    -- This function should return the optimal route between startPoint and endPoint
    -- For now, we'll return a dummy route
    return {
        name = "Sample Route",
        path = {startPoint, endPoint},
        distance = math.random(100, 500)
    }
end

-- Create and return the game instance
return CartographersQuest.new()
