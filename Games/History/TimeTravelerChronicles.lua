-- Time Traveler Chronicles Script
-- Place this in ServerScriptService

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

-- Create the main game module
local TimeTravelerChronicles = {}
TimeTravelerChronicles.__index = TimeTravelerChronicles

function TimeTravelerChronicles.new()
    local self = setmetatable({}, TimeTravelerChronicles)
    
    self.timePeriods = {}
    self.playerData = {}
    self.historicalEvents = {}
    
    -- Create remote events
    self.remotes = {
        TravelToTime = Instance.new("RemoteEvent"),
        InteractWithFigure = Instance.new("RemoteEvent"),
        ParticipateInEvent = Instance.new("RemoteEvent"),
        CollectArtifact = Instance.new("RemoteEvent"),
        CompleteQuest = Instance.new("RemoteEvent")
    }
    
    for name, remote in pairs(self.remotes) do
        remote.Name = name
        remote.Parent = ReplicatedStorage
    end
    
    self:initializeTimePeriods()
    self:setupEventHandlers()
    
    return self
end

-- Initialize time periods
function TimeTravelerChronicles:initializeTimePeriods()
    self.timePeriods = {
        ancient_egypt = {
            name = "Ancient Egypt",
            year = -2500,
            location = "Nile River Valley",
            figures = {
                {name = "Pharaoh Khufu", role = "Ruler", dialogue = {
                    "Welcome, traveler from the future!",
                    "Behold my great pyramid, a monument to eternity.",
                    "The gods have blessed our land with prosperity."
                }},
                {name = "Imhotep", role = "Architect", dialogue = {
                    "Architecture is the art of the gods.",
                    "Each stone tells a story of our civilization.",
                    "Mathematics and astronomy guide our constructions."
                }}
            },
            events = {
                {name = "Pyramid Construction", type = "Building", 
                 description = "Participate in the construction of the Great Pyramid"},
                {name = "Nile Flooding", type = "Natural", 
                 description = "Observe the annual flooding that brings fertility"}
            },
            artifacts = {
                {name = "Scarab Amulet", description = "Symbol of rebirth and protection"},
                {name = "Papyrus Scroll", description = "Ancient hieroglyphic writings"}
            }
        },
        medieval_europe = {
            name = "Medieval Europe",
            year = 1200,
            location = "England",
            figures = {
                {name = "King Richard I", role = "Monarch", dialogue = {
                    "Honor and chivalry guide our actions.",
                    "The Crusades call for brave warriors.",
                    "A king must serve his people."
                }},
                {name = "Eleanor of Aquitaine", role = "Queen", dialogue = {
                    "Power comes not just from the sword.",
                    "Education is the key to influence.",
                    "Women shape history in many ways."
                }}
            },
            events = {
                {name = "Knight's Tournament", type = "Cultural", 
                 description = "Witness medieval martial competitions"},
                {name = "Castle Siege", type = "Military", 
                 description = "Experience medieval warfare tactics"}
            },
            artifacts = {
                {name = "Knight's Helm", description = "Protective armor from the Crusades"},
                {name = "Illuminated Manuscript", description = "Beautifully decorated medieval text"}
            }
        },
        renaissance = {
            name = "Renaissance Italy",
            year = 1500,
            location = "Florence",
            figures = {
                {name = "Leonardo da Vinci", role = "Polymath", dialogue = {
                    "Art and science are two sides of the same coin.",
                    "Observation is the key to understanding.",
                    "The human form is nature's masterpiece."
                }},
                {name = "Michelangelo", role = "Artist", dialogue = {
                    "Sculpture is the art of intelligence.",
                    "Every block of stone has a statue inside.",
                    "Genius is eternal patience."
                }}
            },
            events = {
                {name = "Art Workshop", type = "Cultural", 
                 description = "Learn Renaissance painting techniques"},
                {name = "Scientific Discovery", type = "Educational", 
                 description = "Witness groundbreaking experiments"}
            },
            artifacts = {
                {name = "Artist's Palette", description = "Tools used by Renaissance masters"},
                {name = "Invention Sketches", description = "Da Vinci's engineering designs"}
            }
        }
    }
end

-- Setup event handlers
function TimeTravelerChronicles:setupEventHandlers()
    self.remotes.TravelToTime.OnServerEvent:Connect(function(player, periodKey)
        self:travelToTime(player, periodKey)
    end)
    
    self.remotes.InteractWithFigure.OnServerEvent:Connect(function(player, figureName)
        self:interactWithFigure(player, figureName)
    end)
    
    self.remotes.ParticipateInEvent.OnServerEvent:Connect(function(player, eventName)
        self:participateInEvent(player, eventName)
    end)
    
    self.remotes.CollectArtifact.OnServerEvent:Connect(function(player, artifactName)
        self:collectArtifact(player, artifactName)
    end)
    
    Players.PlayerAdded:Connect(function(player)
        self:initializePlayerData(player)
    end)
end

-- Initialize player data
function TimeTravelerChronicles:initializePlayerData(player)
    self.playerData[player.UserId] = {
        currentPeriod = nil,
        museum = {},
        historicalKnowledge = 0,
        questsCompleted = {},
        conversations = {}
    }
end

-- Travel to time period
function TimeTravelerChronicles:travelToTime(player, periodKey)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    local period = self.timePeriods[periodKey]
    
    if period then
        playerData.currentPeriod = periodKey
        
        -- Create time period environment
        self:createTimePeriodEnvironment(periodKey)
        
        self.remotes.TravelToTime:FireClient(player, {
            success = true,
            period = period
        })
    end
end

-- Create time period environment
function TimeTravelerChronicles:createTimePeriodEnvironment(periodKey)
    -- Clear existing environment
    for _, obj in ipairs(workspace:GetChildren()) do
        if obj:FindFirstChild("HistoricalEnvironment") then
            obj:Destroy()
        end
    end
    
    local period = self.timePeriods[periodKey]
    
    -- Create basic environment based on period
    local environment = Instance.new("Model")
    environment.Name = period.name .. "_Environment"
    
    local tag = Instance.new("BoolValue")
    tag.Name = "HistoricalEnvironment"
    tag.Parent = environment
    
    -- Create ground
    local ground = Instance.new("Part")
    ground.Name = "Ground"
    ground.Size = Vector3.new(200, 1, 200)
    ground.Position = Vector3.new(0, 0, 0)
    ground.Anchored = true
    ground.Parent = environment
    
    -- Add period-specific elements
    if periodKey == "ancient_egypt" then
        ground.BrickColor = BrickColor.new("Sand yellow")
        
        -- Create pyramid
        local pyramid = Instance.new("Part")
        pyramid.Name = "Pyramid"
        pyramid.Size = Vector3.new(50, 50, 50)
        pyramid.Position = Vector3.new(0, 25, 0)
        pyramid.Anchored = true
        pyramid.Parent = environment
    elseif periodKey == "medieval_europe" then
        ground.BrickColor = BrickColor.new("Earth green")
        
        -- Create castle
        local castle = Instance.new("Part")
        castle.Name = "Castle"
        castle.Size = Vector3.new(40, 40, 40)
        castle.Position = Vector3.new(0, 20, 0)
        castle.Anchored = true
        castle.Parent = environment
    elseif periodKey == "renaissance" then
        ground.BrickColor = BrickColor.new("Light stone grey")
        
        -- Create art studio
        local studio = Instance.new("Part")
        studio.Name = "ArtStudio"
        studio.Size = Vector3.new(30, 20, 30)
        studio.Position = Vector3.new(0, 10, 0)
        studio.Anchored = true
        studio.Parent = environment
    end
    
    environment.Parent = workspace
    
    -- Spawn historical figures
    self:spawnHistoricalFigures(periodKey)
end

-- Spawn historical figures
function TimeTravelerChronicles:spawnHistoricalFigures(periodKey)
    local period = self.timePeriods[periodKey]
    
    for _, figure in ipairs(period.figures) do
        local npc = Instance.new("Model")
        npc.Name = figure.name
        
        -- Create basic NPC representation
        local humanoid = Instance.new("Humanoid")
        humanoid.Parent = npc
        
        local part = Instance.new("Part")
        part.Name = "HumanoidRootPart"
        part.Size = Vector3.new(2, 2, 1)
        part.Position = Vector3.new(
            math.random(-20, 20),
            3,
            math.random(-20, 20)
        )
        part.Anchored = true
        part.Parent = npc
        
        -- Add interaction prompt
        local billboard = Instance.new("BillboardGui")
        billboard.Size = UDim2.new(0, 200, 0, 50)
        billboard.StudsOffset = Vector3.new(0, 3, 0)
        billboard.Parent = part
        
        local textLabel = Instance.new("TextLabel")
        textLabel.Size = UDim2.new(1, 0, 1, 0)
        textLabel.Text = figure.name .. "\n" .. figure.role
        textLabel.TextScaled = true
        textLabel.BackgroundTransparency = 1
        textLabel.Parent = billboard
        
        -- Add click detector
        local clickDetector = Instance.new("ClickDetector")
        clickDetector.Parent = part
        
        clickDetector.MouseClick:Connect(function(player)
            self:interactWithFigure(player, figure.name)
        end)
        
        npc.Parent = workspace
    end
end

-- Interact with historical figure
function TimeTravelerChronicles:interactWithFigure(player, figureName)
    local playerData = self.playerData[player.UserId]
    
    if not playerData or not playerData.currentPeriod then
        return
    end
    
    local period = self.timePeriods[playerData.currentPeriod]
    
    for _, figure in ipairs(period.figures) do
        if figure.name == figureName then
            -- Get random dialogue
            local dialogue = figure.dialogue[math.random(#figure.dialogue)]
            
            -- Track conversation
            if not playerData.conversations[figureName] then
                playerData.conversations[figureName] = 0
            end
            
            playerData.conversations[figureName] = playerData.conversations[figureName] + 1
            playerData.historicalKnowledge = playerData.historicalKnowledge + 10
            
            self.remotes.InteractWithFigure:FireClient(player, {
                figure = figure,
                dialogue = dialogue,
                knowledge = 10
            })
            
            break
        end
    end
end

-- Participate in historical event
function TimeTravelerChronicles:participateInEvent(player, eventName)
    local playerData = self.playerData[player.UserId]
    
    if not playerData or not playerData.currentPeriod then
        return
    end
    
    local period = self.timePeriods[playerData.currentPeriod]
    
    for _, event in ipairs(period.events) do
        if event.name == eventName then
            -- Create event challenge
            local challenge = self:createEventChallenge(event)
            
            -- Simulate event participation
            playerData.historicalKnowledge = playerData.historicalKnowledge + 25
            table.insert(playerData.questsCompleted, eventName)
            
            self.remotes.ParticipateInEvent:FireClient(player, {
                event = event,
                challenge = challenge,
                success = true,
                knowledge = 25
            })
            
            break
        end
    end
end

-- Create event challenge
function TimeTravelerChronicles:createEventChallenge(event)
    local challenges = {
        ["Pyramid Construction"] = {
            type = "puzzle",
            description = "Help organize workers and resources",
            objective = "Place stone blocks in correct positions"
        },
        ["Knight's Tournament"] = {
            type = "skill",
            description = "Test your medieval combat skills",
            objective = "Complete jousting challenge"
        },
        ["Art Workshop"] = {
            type = "creative",
            description = "Learn Renaissance painting techniques",
            objective = "Mix colors to match masterpiece"
        }
    }
    
    return challenges[event.name] or {
        type = "observation",
        description = "Observe and learn from the event",
        objective = "Watch and take notes"
    }
end

-- Collect artifact
function TimeTravelerChronicles:collectArtifact(player, artifactName)
    local playerData = self.playerData[player.UserId]
    
    if not playerData or not playerData.currentPeriod then
        return
    end
    
    local period = self.timePeriods[playerData.currentPeriod]
    
    for _, artifact in ipairs(period.artifacts) do
        if artifact.name == artifactName then
            -- Add to museum collection
            table.insert(playerData.museum, {
                name = artifact.name,
                description = artifact.description,
                period = period.name,
                year = period.year
            })
            
            playerData.historicalKnowledge = playerData.historicalKnowledge + 15
            
            self.remotes.CollectArtifact:FireClient(player, {
                artifact = artifact,
                knowledge = 15
            })
            
            break
        end
    end
end

-- Create and return the game instance
return TimeTravelerChronicles.new()