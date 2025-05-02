-- Ecosystem Explorer Script
-- Place this in ServerScriptService

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

-- Create the main game module
local EcosystemExplorer = {}
EcosystemExplorer.__index = EcosystemExplorer

function EcosystemExplorer.new()
    local self = setmetatable({}, EcosystemExplorer)
    
    self.biomes = {}
    self.playerData = {}
    self.wildlife = {}
    self.weather = {
        temperature = 20,
        precipitation = "none",
        windSpeed = 5
    }
    
    -- Create remote events
    self.remotes = {
        ExploreBiome = Instance.new("RemoteEvent"),
        TakePhoto = Instance.new("RemoteEvent"),
        CompleteMission = Instance.new("RemoteEvent"),
        UpdateWeather = Instance.new("RemoteEvent"),
        IdentifySpecies = Instance.new("RemoteEvent")
    }
    
    for name, remote in pairs(self.remotes) do
        remote.Name = name
        remote.Parent = ReplicatedStorage
    end
    
    self:initializeBiomes()
    self:setupEventHandlers()
    self:startWeatherSystem()
    
    return self
end

-- Initialize biomes
function EcosystemExplorer:initializeBiomes()
    self.biomes = {
        forest = {
            name = "Temperate Forest",
            temperature = 15,
            humidity = 70,
            species = {
                flora = {"Oak Tree", "Maple Tree", "Fern", "Mushroom"},
                fauna = {"Deer", "Fox", "Squirrel", "Robin"}
            },
            foodWeb = {
                producers = {"Oak Tree", "Maple Tree", "Fern"},
                primaryConsumers = {"Deer", "Squirrel"},
                secondaryConsumers = {"Fox"},
                decomposers = {"Mushroom"}
            }
        },
        ocean = {
            name = "Coral Reef",
            temperature = 25,
            salinity = 35,
            species = {
                flora = {"Coral", "Seaweed", "Kelp", "Phytoplankton"},
                fauna = {"Clownfish", "Sea Turtle", "Shark", "Octopus"}
            },
            foodWeb = {
                producers = {"Coral", "Seaweed", "Phytoplankton"},
                primaryConsumers = {"Clownfish", "Sea Turtle"},
                secondaryConsumers = {"Shark"},
                decomposers = {"Sea Cucumber"}
            }
        },
        desert = {
            name = "Sandy Desert",
            temperature = 35,
            humidity = 20,
            species = {
                flora = {"Cactus", "Joshua Tree", "Sage", "Tumbleweed"},
                fauna = {"Camel", "Lizard", "Scorpion", "Roadrunner"}
            },
            foodWeb = {
                producers = {"Cactus", "Sage"},
                primaryConsumers = {"Camel", "Lizard"},
                secondaryConsumers = {"Roadrunner"},
                decomposers = {"Dung Beetle"}
            }
        }
    }
end

-- Setup event handlers
function EcosystemExplorer:setupEventHandlers()
    self.remotes.ExploreBiome.OnServerEvent:Connect(function(player, biomeName)
        self:exploreBiome(player, biomeName)
    end)
    
    self.remotes.TakePhoto.OnServerEvent:Connect(function(player, species)
        self:takePhoto(player, species)
    end)
    
    self.remotes.CompleteMission.OnServerEvent:Connect(function(player, missionType)
        self:completeMission(player, missionType)
    end)
    
    self.remotes.IdentifySpecies.OnServerEvent:Connect(function(player, species)
        self:identifySpecies(player, species)
    end)
    
    Players.PlayerAdded:Connect(function(player)
        self:initializePlayerData(player)
    end)
end

-- Initialize player data
function EcosystemExplorer:initializePlayerData(player)
    self.playerData[player.UserId] = {
        currentBiome = nil,
        discoveredSpecies = {},
        photoAlbum = {},
        conservationPoints = 0,
        missions = {}
    }
end

-- Explore biome
function EcosystemExplorer:exploreBiome(player, biomeName)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    local biome = self.biomes[biomeName]
    
    if biome then
        playerData.currentBiome = biomeName
        
        -- Spawn wildlife for the biome
        self:spawnWildlife(biomeName)
        
        -- Update weather for the biome
        self:updateWeather(biome)
        
        self.remotes.ExploreBiome:FireClient(player, {
            success = true,
            biome = biome,
            weather = self.weather
        })
    end
end

-- Spawn wildlife
function EcosystemExplorer:spawnWildlife(biomeName)
    local biome = self.biomes[biomeName]
    
    if not biome then
        return
    end
    
    -- Clear existing wildlife
    for _, animal in ipairs(workspace:GetChildren()) do
        if animal:IsA("Model") and animal:FindFirstChild("Wildlife") then
            animal:Destroy()
        end
    end
    
    -- Spawn new wildlife
    for _, species in ipairs(biome.species.fauna) do
        local animal = Instance.new("Model")
        animal.Name = species
        
        -- Create basic animal representation
        local part = Instance.new("Part")
        part.Name = "Body"
        part.Size = Vector3.new(2, 2, 3)
        part.Position = Vector3.new(
            math.random(-50, 50),
            2,
            math.random(-50, 50)
        )
        part.Anchored = false
        part.Parent = animal
        
        -- Add species identifier
        local speciesTag = Instance.new("StringValue")
        speciesTag.Name = "Wildlife"
        speciesTag.Value = species
        speciesTag.Parent = animal
        
        -- Add basic AI behavior
        local humanoid = Instance.new("Humanoid")
        humanoid.Parent = animal
        
        animal.Parent = workspace
        
        -- Simple wandering behavior
        task.spawn(function()
            while animal.Parent do
                local destination = part.Position + Vector3.new(
                    math.random(-10, 10),
                    0,
                    math.random(-10, 10)
                )
                humanoid:MoveTo(destination)
                wait(math.random(5, 10))
            end
        end)
    end
end

-- Take photo of species
function EcosystemExplorer:takePhoto(player, species)
    local playerData = self.playerData[player.UserId]
    
    if not playerData or not playerData.currentBiome then
        return
    end
    
    local biome = self.biomes[playerData.currentBiome]
    
    -- Check if species exists in current biome
    local found = false
    
    for _, category in pairs(biome.species) do
        if table.find(category, species) then
            found = true
            break
        end
    end
    
    if found then
        -- Add to photo album
        table.insert(playerData.photoAlbum, {
            species = species,
            biome = playerData.currentBiome,
            timestamp = os.time()
        })
        
        -- Check if new species discovered
        if not table.find(playerData.discoveredSpecies, species) then
            table.insert(playerData.discoveredSpecies, species)
            playerData.conservationPoints = playerData.conservationPoints + 10
            
            self.remotes.TakePhoto:FireClient(player, {
                success = true,
                newDiscovery = true,
                species = species,
                points = 10
            })
        else
            self.remotes.TakePhoto:FireClient(player, {
                success = true,
                newDiscovery = false,
                species = species
            })
        end
    else
        self.remotes.TakePhoto:FireClient(player, {
            success = false,
            message = "Species not found in this biome"
        })
    end
end

-- Complete mission
function EcosystemExplorer:completeMission(player, missionType)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    local missions = {
        food_web = {
            name = "Complete Food Web",
            objective = "Identify all members of the food web",
            reward = 50
        },
        conservation = {
            name = "Conservation Effort",
            objective = "Document endangered species",
            reward = 100
        },
        habitat_restoration = {
            name = "Habitat Restoration",
            objective = "Help restore native plants",
            reward = 75
        }
    }
    
    local mission = missions[missionType]
    
    if mission then
        -- Simulate mission completion
        playerData.conservationPoints = playerData.conservationPoints + mission.reward
        table.insert(playerData.missions, {
            type = missionType,
            completedAt = os.time()
        })
        
        self.remotes.CompleteMission:FireClient(player, {
            success = true,
            mission = mission,
            reward = mission.reward
        })
    end
end

-- Update weather system
function EcosystemExplorer:updateWeather(biome)
    if biome then
        self.weather.temperature = biome.temperature + math.random(-5, 5)
        
        -- Determine precipitation based on biome
        if biome.name == "Temperate Forest" then
            self.weather.precipitation = math.random() < 0.3 and "rain" or "none"
        elseif biome.name == "Sandy Desert" then
            self.weather.precipitation = math.random() < 0.05 and "rain" or "none"
        else
            self.weather.precipitation = "none"
        end
        
        self.weather.windSpeed = math.random(0, 20)
    end
end

-- Start weather system
function EcosystemExplorer:startWeatherSystem()
    RunService.Heartbeat:Connect(function()
        -- Update weather periodically
        if tick() % 60 < 1 then  -- Every minute
            if next(self.playerData) then  -- If players are in game
                for _, playerData in pairs(self.playerData) do
                    if playerData.currentBiome then
                        local biome = self.biomes[playerData.currentBiome]
                        self:updateWeather(biome)
                        break
                    end
                end
                
                -- Update all clients
                for _, player in ipairs(Players:GetPlayers()) do
                    self.remotes.UpdateWeather:FireClient(player, self.weather)
                end
            end
        end
    end)
end

-- Identify species
function EcosystemExplorer:identifySpecies(player, species)
    local playerData = self.playerData[player.UserId]
    
    if not playerData or not playerData.currentBiome then
        return
    end
    
    local biome = self.biomes[playerData.currentBiome]
    local speciesInfo = {
        name = species,
        role = "",
        description = ""
    }
    
    -- Determine species role in ecosystem
    for role, speciesList in pairs(biome.foodWeb) do
        if table.find(speciesList, species) then
            speciesInfo.role = role
            break
        end
    end
    
    -- Add description based on role
    if speciesInfo.role == "producers" then
        speciesInfo.description = "Produces energy through photosynthesis"
    elseif speciesInfo.role == "primaryConsumers" then
        speciesInfo.description = "Herbivore that eats plants"
    elseif speciesInfo.role == "secondaryConsumers" then
        speciesInfo.description = "Predator that hunts other animals"
    elseif speciesInfo.role == "decomposers" then
        speciesInfo.description = "Breaks down dead organic matter"
    end
    
    self.remotes.IdentifySpecies:FireClient(player, speciesInfo)
end

-- Create and return the game instance
return EcosystemExplorer.new()