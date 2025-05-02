-- Global Explorer VR Script
-- Place this in ServerScriptService

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

-- Create the main game module
local GlobalExplorerVR = {}
GlobalExplorerVR.__index = GlobalExplorerVR

function GlobalExplorerVR.new()
    local self = setmetatable({}, GlobalExplorerVR)
    
    self.locations = {}
    self.playerData = {}
    
    -- Create remote events
    self.remotes = {
        TravelTo = Instance.new("RemoteEvent"),
        GeographyChallenge = Instance.new("RemoteEvent"),
        CulturalLearning = Instance.new("RemoteEvent"),
        MapReading = Instance.new("RemoteEvent"),
        ClimateSimulation = Instance.new("RemoteEvent"),
        TradeRoutePuzzle = Instance.new("RemoteEvent")
    }
    
    for name, remote in pairs(self.remotes) do
        remote.Name = name
        remote.Parent = ReplicatedStorage
    end
    
    self:initializeLocations()
    self:setupEventHandlers()
    
    return self
end

-- Initialize locations
function GlobalExplorerVR:initializeLocations()
    self.locations = {
        paris = {
            country = "France",
            landmark = "Eiffel Tower",
            coordinates = {lat = 48.8584, lon = 2.2945},
            climate = "Temperate",
            culture = {
                language = "French",
                cuisine = {"Croissant", "Baguette", "Cheese"},
                traditions = {"Bastille Day", "Fashion Week"}
            },
            geography = {
                terrain = "Urban plain",
                river = "Seine",
                elevation = 35
            }
        },
        tokyo = {
            country = "Japan",
            landmark = "Tokyo Skytree",
            coordinates = {lat = 35.6895, lon = 139.6917},
            climate = "Humid Subtropical",
            culture = {
                language = "Japanese",
                cuisine = {"Sushi", "Ramen", "Tempura"},
                traditions = {"Cherry Blossom Festival", "New Year Celebrations"}
            },
            geography = {
                terrain = "Coastal plain",
                bay = "Tokyo Bay",
                elevation = 40
            }
        },
        cairo = {
            country = "Egypt",
            landmark = "Great Pyramids",
            coordinates = {lat = 30.0444, lon = 31.2357},
            climate = "Desert",
            culture = {
                language = "Arabic",
                cuisine = {"Falafel", "Koshari", "Baklava"},
                traditions = {"Ramadan", "Sham el-Nessim"}
            },
            geography = {
                terrain = "Desert",
                river = "Nile",
                elevation = 23
            }
        },
        rio = {
            country = "Brazil",
            landmark = "Christ the Redeemer",
            coordinates = {lat = -22.9068, lon = -43.1729},
            climate = "Tropical",
            culture = {
                language = "Portuguese",
                cuisine = {"Feijoada", "Churrasco", "Brigadeiro"},
                traditions = {"Carnival", "Football Culture"}
            },
            geography = {
                terrain = "Coastal mountains",
                bay = "Guanabara Bay",
                elevation = 2
            }
        }
    }
end

-- Setup event handlers
function GlobalExplorerVR:setupEventHandlers()
    self.remotes.TravelTo.OnServerEvent:Connect(function(player, locationKey)
        self:travelTo(player, locationKey)
    end)
    
    self.remotes.GeographyChallenge.OnServerEvent:Connect(function(player, challengeType, answer)
        self:geographyChallenge(player, challengeType, answer)
    end)
    
    self.remotes.CulturalLearning.OnServerEvent:Connect(function(player, locationKey)
        self:culturalLearning(player, locationKey)
    end)
    
    self.remotes.MapReading.OnServerEvent:Connect(function(player)
        self:mapReadingExercise(player)
    end)
    
    self.remotes.ClimateSimulation.OnServerEvent:Connect(function(player, locationKey)
        self:climateSimulation(player, locationKey)
    end)
    
    self.remotes.TradeRoutePuzzle.OnServerEvent:Connect(function(player, solution)
        self:tradeRoutePuzzle(player, solution)
    end)
    
    Players.PlayerAdded:Connect(function(player)
        self:initializePlayerData(player)
    end)
end

-- Initialize player data
function GlobalExplorerVR:initializePlayerData(player)
    self.playerData[player.UserId] = {
        currentLocation = nil,
        visitedLocations = {},
        geographySkills = {
            mapReading = 1,
            climateKnowledge = 1,
            culturalAwareness = 1,
            navigation = 1
        },
        passportStamps = {},
        achievements = {},
        experience = 0
    }
end

-- Travel to location
function GlobalExplorerVR:travelTo(player, locationKey)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    local location = self.locations[locationKey]
    
    if location then
        playerData.currentLocation = locationKey
        
        -- Add to visited locations
        if not table.find(playerData.visitedLocations, locationKey) then
            table.insert(playerData.visitedLocations, locationKey)
            table.insert(playerData.passportStamps, {
                location = locationKey,
                date = os.date("%Y-%m-%d"),
                landmark = location.landmark
            })
        end
        
        -- Create location environment
        self:createLocationEnvironment(locationKey)
        
        self.remotes.TravelTo:FireClient(player, {
            success = true,
            location = location
        })
    end
end

-- Create location environment
function GlobalExplorerVR:createLocationEnvironment(locationKey)
    -- Clear existing environment
    for _, obj in ipairs(workspace:GetChildren()) do
        if obj:FindFirstChild("GlobalLocation") then
            obj:Destroy()
        end
    end
    
    local location = self.locations[locationKey]
    local environment = Instance.new("Model")
    environment.Name = location.country .. "_Environment"
    
    local tag = Instance.new("BoolValue")
    tag.Name = "GlobalLocation"
    tag.Parent = environment
    
    -- Create landmark
    local landmark = Instance.new("Part")
    landmark.Name = location.landmark
    landmark.Anchored = true
    landmark.Parent = environment
    
    -- Set landmark properties based on location
    if locationKey == "paris" then
        landmark.Size = Vector3.new(10, 50, 10)
        landmark.Position = Vector3.new(0, 25, 0)
        landmark.BrickColor = BrickColor.new("Dark stone grey")
        
    elseif locationKey == "tokyo" then
        landmark.Size = Vector3.new(15, 60, 15)
        landmark.Position = Vector3.new(0, 30, 0)
        landmark.BrickColor = BrickColor.new("White")
        
    elseif locationKey == "cairo" then
        landmark.Size = Vector3.new(50, 40, 50)
        landmark.Position = Vector3.new(0, 20, 0)
        landmark.BrickColor = BrickColor.new("Sand yellow")
        
    elseif locationKey == "rio" then
        landmark.Size = Vector3.new(5, 30, 5)
        landmark.Position = Vector3.new(0, 15, 0)
        landmark.BrickColor = BrickColor.new("Light stone grey")
    end
    
    -- Add information display
    local billboard = Instance.new("BillboardGui")
    billboard.Size = UDim2.new(0, 300, 0, 100)
    billboard.StudsOffset = Vector3.new(0, 10, 0)
    billboard.Parent = landmark
    
    local label = Instance.new("TextLabel")
    label.Size = UDim2.new(1, 0, 1, 0)
    label.Text = location.landmark .. "\n" .. location.country
    label.TextScaled = true
    label.BackgroundTransparency = 0.5
    label.Parent = billboard
    
    environment.Parent = workspace
end

-- Geography challenge
function GlobalExplorerVR:geographyChallenge(player, challengeType, answer)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    local challenges = {
        capitals = {
            {question = "What is the capital of France?", answer = "Paris"},
            {question = "What is the capital of Japan?", answer = "Tokyo"},
            {question = "What is the capital of Egypt?", answer = "Cairo"}
        },
        flags = {
            {question = "Which country has a red circle on a white background?", answer = "Japan"},
            {question = "Which country has a green, white, and red vertical tricolor?", answer = "Italy"}
        },
        terrain = {
            {question = "Which continent has the Sahara Desert?", answer = "Africa"},
            {question = "What is the longest river in the world?", answer = "Nile"}
        }
    }
    
    local challenge = challenges[challengeType][math.random(#challenges[challengeType])]
    
    if answer == challenge.answer then
        playerData.geographySkills.mapReading = playerData.geographySkills.mapReading + 1
        playerData.experience = playerData.experience + 20
        
        self.remotes.GeographyChallenge:FireClient(player, {
            success = true,
            correct = true,
            xpReward = 20
        })
    else
        self.remotes.GeographyChallenge:FireClient(player, {
            success = true,
            correct = false,
            answer = challenge.answer
        })
    end
end

-- Cultural learning
function GlobalExplorerVR:culturalLearning(player, locationKey)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    local location = self.locations[locationKey]
    
    if location then
        playerData.geographySkills.culturalAwareness = playerData.geographySkills.culturalAwareness + 1
        playerData.experience = playerData.experience + 15
        
        -- Create cultural lesson data
        local phrases = {
            french = {hello = "Bonjour", thanks = "Merci", goodbye = "Au revoir"},
            japanese = {hello = "Konnichiwa", thanks = "Arigatou", goodbye = "Sayonara"},
            arabic = {hello = "Marhaba", thanks = "Shukran", goodbye = "Ma'a salama"},
            portuguese = {hello = "Olá", thanks = "Obrigado", goodbye = "Tchau"}
        }
        
        self.remotes.CulturalLearning:FireClient(player, {
            success = true,
            culture = location.culture,
            phrases = phrases[location.culture.language:lower()],
            xpReward = 15
        })
    end
end

-- Map reading exercise
function GlobalExplorerVR:mapReadingExercise(player)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    -- Generate map challenge
    local challenge = {
        startLocation = "Paris",
        endLocation = "Berlin",
        distance = 1050,
        directions = {"East from Paris", "Cross through Belgium", "Enter Germany"}
    }
    
    playerData.geographySkills.mapReading = playerData.geographySkills.mapReading + 1
    playerData.geographySkills.navigation = playerData.geographySkills.navigation + 1
    playerData.experience = playerData.experience + 25
    
    self.remotes.MapReading:FireClient(player, {
        success = true,
        challenge = challenge,
        xpReward = 25
    })
end

-- Climate simulation
function GlobalExplorerVR:climateSimulation(player, locationKey)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    local location = self.locations[locationKey]
    
    if location then
        local climateData = {
            Temperate = {
                seasons = {"Spring", "Summer", "Autumn", "Winter"},
                avgTemp = {15, 25, 15, 5},
                precipitation = "Moderate year-round"
            },
            ["Humid Subtropical"] = {
                seasons = {"Mild Winter", "Hot Summer"},
                avgTemp = {10, 30},
                precipitation = "High in summer"
            },
            Desert = {
                seasons = {"Warm", "Hot"},
                avgTemp = {25, 40},
                precipitation = "Very low"
            },
            Tropical = {
                seasons = {"Wet", "Dry"},
                avgTemp = {28, 32},
                precipitation = "Heavy in wet season"
            }
        }
        
        local climate = climateData[location.climate]
        
        if climate then
            playerData.geographySkills.climateKnowledge = playerData.geographySkills.climateKnowledge + 1
            playerData.experience = playerData.experience + 20
            
            self.remotes.ClimateSimulation:FireClient(player, {
                success = true,
                climate = climate,
                xpReward = 20
            })
        end
    end
end

-- Trade route puzzle
function GlobalExplorerVR:tradeRoutePuzzle(player, solution)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    -- Define trade routes
    local routes = {
        {from = "Tokyo", to = "Los Angeles", distance = 8800, cost = 5000, ratio = 1.76},
        {from = "Paris", to = "New York", distance = 5800, cost = 3500, ratio = 1.66},
        {from = "Cairo", to = "Mumbai", distance = 4000, cost = 2800, ratio = 1.43}
    }
    
    -- Check if solution is correct (lowest ratio = most efficient)
    if solution == 3 then  -- Cairo to Mumbai has best ratio
        playerData.geographySkills.navigation = playerData.geographySkills.navigation + 2
        playerData.experience = playerData.experience + 30
        
        self.remotes.TradeRoutePuzzle:FireClient(player, {
            success = true,
            correct = true,
            xpReward = 30
        })
    else
        self.remotes.TradeRoutePuzzle:FireClient(player, {
            success = true,
            correct = false,
            message = "Not the most efficient route"
        })
    end
end

-- Create and return the game instance
return GlobalExplorerVR.new()