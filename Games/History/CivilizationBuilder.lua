-- Civilization Builder Script
-- Place this in ServerScriptService

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

-- Create the main game module
local CivilizationBuilder = {}
CivilizationBuilder.__index = CivilizationBuilder

function CivilizationBuilder.new()
    local self = setmetatable({}, CivilizationBuilder)
    
    self.civilizations = {}
    self.playerData = {}
    self.techTree = {}
    self.buildings = {}
    
    -- Create remote events
    self.remotes = {
        StartCivilization = Instance.new("RemoteEvent"),
        BuildStructure = Instance.new("RemoteEvent"),
        ResearchTechnology = Instance.new("RemoteEvent"),
        DiplomaticAction = Instance.new("RemoteEvent"),
        GatherResources = Instance.new("RemoteEvent"),
        AdvanceEra = Instance.new("RemoteEvent")
    }
    
    for name, remote in pairs(self.remotes) do
        remote.Name = name
        remote.Parent = ReplicatedStorage
    end
    
    self:initializeCivilizations()
    self:initializeTechTree()
    self:setupEventHandlers()
    self:startResourceGeneration()
    
    return self
end

-- Initialize civilizations
function CivilizationBuilder:initializeCivilizations()
    self.civilizations = {
        mesopotamia = {
            name = "Mesopotamia",
            startYear = -3000,
            startingTech = {"Agriculture", "Writing", "Wheel"},
            uniqueTraits = {"River Valley", "Irrigation Mastery"},
            resources = {food = 100, wood = 50, stone = 30, gold = 20}
        },
        egypt = {
            name = "Ancient Egypt",
            startYear = -3100,
            startingTech = {"Hieroglyphics", "Agriculture", "Architecture"},
            uniqueTraits = {"Nile Flood Bonus", "Monument Builders"},
            resources = {food = 120, wood = 40, stone = 60, gold = 30}
        },
        greece = {
            name = "Ancient Greece",
            startYear = -800,
            startingTech = {"Philosophy", "Democracy", "Mathematics"},
            uniqueTraits = {"Cultural Influence", "Naval Expertise"},
            resources = {food = 90, wood = 60, stone = 40, gold = 40}
        },
        rome = {
            name = "Roman Empire",
            startYear = -753,
            startingTech = {"Engineering", "Law", "Military Organization"},
            uniqueTraits = {"Road Building", "Legion Strength"},
            resources = {food = 100, wood = 50, stone = 70, gold = 50}
        }
    }
end

-- Initialize technology tree
function CivilizationBuilder:initializeTechTree()
    self.techTree = {
        ancient = {
            {name = "Agriculture", cost = 50, prerequisites = {}, 
             effects = "Increases food production by 25%"},
            {name = "Writing", cost = 75, prerequisites = {}, 
             effects = "Enables record keeping and education"},
            {name = "Wheel", cost = 60, prerequisites = {}, 
             effects = "Improves transportation and trade"},
            {name = "Architecture", cost = 100, prerequisites = {"Writing"}, 
             effects = "Enables advanced building construction"}
        },
        classical = {
            {name = "Mathematics", cost = 150, prerequisites = {"Writing"}, 
             effects = "Improves engineering and science"},
            {name = "Philosophy", cost = 120, prerequisites = {"Writing"}, 
             effects = "Increases cultural influence"},
            {name = "Engineering", cost = 200, prerequisites = {"Mathematics", "Architecture"}, 
             effects = "Enables aqueducts and advanced structures"},
            {name = "Iron Working", cost = 180, prerequisites = {"Mining"}, 
             effects = "Improves military and tools"}
        },
        medieval = {
            {name = "Feudalism", cost = 250, prerequisites = {"Law"}, 
             effects = "Enables castle construction"},
            {name = "Navigation", cost = 300, prerequisites = {"Mathematics"}, 
             effects = "Improves naval exploration"},
            {name = "Printing Press", cost = 400, prerequisites = {"Writing", "Engineering"}, 
             effects = "Spreads knowledge faster"}
        }
    }
end

-- Setup event handlers
function CivilizationBuilder:setupEventHandlers()
    self.remotes.StartCivilization.OnServerEvent:Connect(function(player, civKey)
        self:startCivilization(player, civKey)
    end)
    
    self.remotes.BuildStructure.OnServerEvent:Connect(function(player, buildingType, position)
        self:buildStructure(player, buildingType, position)
    end)
    
    self.remotes.ResearchTechnology.OnServerEvent:Connect(function(player, techName)
        self:researchTechnology(player, techName)
    end)
    
    self.remotes.DiplomaticAction.OnServerEvent:Connect(function(player, targetCiv, action)
        self:diplomaticAction(player, targetCiv, action)
    end)
    
    Players.PlayerAdded:Connect(function(player)
        self:initializePlayerData(player)
    end)
end

-- Initialize player data
function CivilizationBuilder:initializePlayerData(player)
    self.playerData[player.UserId] = {
        civilization = nil,
        year = 0,
        population = 100,
        buildings = {},
        technologies = {},
        diplomacy = {},
        resources = {food = 0, wood = 0, stone = 0, gold = 0}
    }
end

-- Start civilization
function CivilizationBuilder:startCivilization(player, civKey)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    local civ = self.civilizations[civKey]
    
    if civ then
        playerData.civilization = civKey
        playerData.year = civ.startYear
        playerData.resources = table.clone(civ.resources)
        
        -- Add starting technologies
        for _, tech in ipairs(civ.startingTech) do
            playerData.technologies[tech] = true
        end
        
        -- Create starting settlement
        self:createStartingSettlement(player)
        
        self.remotes.StartCivilization:FireClient(player, {
            success = true,
            civilization = civ,
            year = playerData.year
        })
    end
end

-- Create starting settlement
function CivilizationBuilder:createStartingSettlement(player)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    -- Create settlement center
    local settlement = Instance.new("Model")
    settlement.Name = player.Name .. "_Settlement"
    
    -- Create main building
    local townCenter = Instance.new("Part")
    townCenter.Name = "TownCenter"
    townCenter.Size = Vector3.new(10, 10, 10)
    townCenter.Position = Vector3.new(0, 5, 0)
    townCenter.Anchored = true
    townCenter.Parent = settlement
    
    -- Add settlement marker
    local marker = Instance.new("BillboardGui")
    marker.Size = UDim2.new(0, 200, 0, 50)
    marker.StudsOffset = Vector3.new(0, 8, 0)
    marker.Parent = townCenter
    
    local label = Instance.new("TextLabel")
    label.Size = UDim2.new(1, 0, 1, 0)
    label.Text = playerData.civilization .. " Settlement"
    label.TextScaled = true
    label.BackgroundTransparency = 1
    label.Parent = marker
    
    settlement.Parent = workspace
    
    -- Add to player's buildings
    table.insert(playerData.buildings, {
        type = "Town Center",
        position = townCenter.Position,
        level = 1
    })
end

-- Build structure
function CivilizationBuilder:buildStructure(player, buildingType, position)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    local buildings = {
        Farm = {cost = {wood = 20, stone = 10}, production = {food = 10}},
        Quarry = {cost = {wood = 30, stone = 20}, production = {stone = 8}},
        ["Lumber Mill"] = {cost = {wood = 40, stone = 15}, production = {wood = 12}},
        Temple = {cost = {wood = 30, stone = 50, gold = 30}, bonus = "Culture"},
        Barracks = {cost = {wood = 50, stone = 40, gold = 20}, bonus = "Military"},
        Library = {cost = {wood = 40, stone = 40, gold = 40}, bonus = "Research"}
    }
    
    local building = buildings[buildingType]
    
    if building then
        -- Check if player can afford
        local canAfford = true
        
        for resource, amount in pairs(building.cost) do
            if playerData.resources[resource] < amount then
                canAfford = false
                break
            end
        end
        
        if canAfford then
            -- Deduct resources
            for resource, amount in pairs(building.cost) do
                playerData.resources[resource] = playerData.resources[resource] - amount
            end
            
            -- Create building
            local buildingPart = Instance.new("Part")
            buildingPart.Name = buildingType
            buildingPart.Size = Vector3.new(8, 8, 8)
            buildingPart.Position = position
            buildingPart.Anchored = true
            buildingPart.Parent = workspace
            
            -- Add to player's buildings
            table.insert(playerData.buildings, {
                type = buildingType,
                position = position,
                level = 1
            })
            
            self.remotes.BuildStructure:FireClient(player, {
                success = true,
                building = buildingType
            })
        else
            self.remotes.BuildStructure:FireClient(player, {
                success = false,
                message = "Not enough resources!"
            })
        end
    end
end

-- Research technology
function CivilizationBuilder:researchTechnology(player, techName)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    -- Find technology
    local techFound = nil
    local era = nil
    
    for eraKey, techs in pairs(self.techTree) do
        for _, tech in ipairs(techs) do
            if tech.name == techName then
                techFound = tech
                era = eraKey
                break
            end
        end
        if techFound then break end
    end
    
    if techFound then
        -- Check prerequisites
        local hasPrereqs = true
        
        for _, prereq in ipairs(techFound.prerequisites) do
            if not playerData.technologies[prereq] then
                hasPrereqs = false
                break
            end
        end
        
        -- Check cost
        if hasPrereqs and playerData.resources.gold >= techFound.cost then
            playerData.resources.gold = playerData.resources.gold - techFound.cost
            playerData.technologies[techName] = true
            
            self.remotes.ResearchTechnology:FireClient(player, {
                success = true,
                technology = techFound
            })
        else
            self.remotes.ResearchTechnology:FireClient(player, {
                success = false,
                message = hasPrereqs and "Not enough gold!" or "Missing prerequisites!"
            })
        end
    end
end

-- Diplomatic action
function CivilizationBuilder:diplomaticAction(player, targetCiv, action)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    if action == "trade" then
        playerData.diplomacy[targetCiv] = "Trade Partner"
        
        -- Increase resources
        playerData.resources.gold = playerData.resources.gold + 20
        
        self.remotes.DiplomaticAction:FireClient(player, {
            success = true,
            action = action,
            target = targetCiv
        })
    elseif action == "alliance" then
        if playerData.diplomacy[targetCiv] == "Trade Partner" then
            playerData.diplomacy[targetCiv] = "Ally"
            
            self.remotes.DiplomaticAction:FireClient(player, {
                success = true,
                action = action,
                target = targetCiv
            })
        else
            self.remotes.DiplomaticAction:FireClient(player, {
                success = false,
                message = "Must be trade partners first!"
            })
        end
    elseif action == "war" then
        playerData.diplomacy[targetCiv] = "At War"
        
        self.remotes.DiplomaticAction:FireClient(player, {
            success = true,
            action = action,
            target = targetCiv
        })
    end
end

-- Start resource generation
function CivilizationBuilder:startResourceGeneration()
    RunService.Heartbeat:Connect(function()
        -- Update resources every 10 seconds
        if tick() % 10 < 0.1 then
            for _, playerData in pairs(self.playerData) do
                if playerData.civilization then
                    -- Base production
                    local production = {
                        food = 5,
                        wood = 3,
                        stone = 2,
                        gold = 1
                    }
                    
                    -- Add building bonuses
                    for _, building in ipairs(playerData.buildings) do
                        if building.type == "Farm" then
                            production.food = production.food + 10
                        elseif building.type == "Quarry" then
                            production.stone = production.stone + 8
                        elseif building.type == "Lumber Mill" then
                            production.wood = production.wood + 12
                        end
                    end
                    
                    -- Update resources
                    for resource, amount in pairs(production) do
                        playerData.resources[resource] = playerData.resources[resource] + amount
                    end
                    
                    -- Update population
                    playerData.population = playerData.population + math.floor(playerData.resources.food / 100)
                    
                    -- Advance year
                    playerData.year = playerData.year + 1
                end
            end
        end
    end)
end

-- Create and return the game instance
return CivilizationBuilder.new()