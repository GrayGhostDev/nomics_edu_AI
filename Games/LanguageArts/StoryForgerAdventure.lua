-- Story Forge Adventure Script
-- Place this in ServerScriptService

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

-- Create the main game module
local StoryForgeAdventure = {}
StoryForgeAdventure.__index = StoryForgeAdventure

function StoryForgeAdventure.new()
    local self = setmetatable({}, StoryForgeAdventure)
    
    self.storyWorlds = {}
    self.playerData = {}
    self.writingChallenges = {}
    self.grammarEnemies = {}
    
    -- Create remote events
    self.remotes = {
        EnterWorld = Instance.new("RemoteEvent"),
        CompleteChallenge = Instance.new("RemoteEvent"),
        GrammarBattle = Instance.new("RemoteEvent"),
        CreateCharacter = Instance.new("RemoteEvent"),
        WriteStory = Instance.new("RemoteEvent"),
        CreatePoem = Instance.new("RemoteEvent")
    }
    
    for name, remote in pairs(self.remotes) do
        remote.Name = name
        remote.Parent = ReplicatedStorage
    end
    
    self:initializeStoryWorlds()
    self:initializeGrammarEnemies()
    self:setupEventHandlers()
    
    return self
end

-- Initialize story worlds
function StoryForgeAdventure:initializeStoryWorlds()
    self.storyWorlds = {
        fantasy = {
            name = "Enchanted Kingdoms",
            elements = {"dragons", "magic", "castles", "quests"},
            writingPrompts = {
                "A young wizard discovers a hidden power...",
                "The dragon's egg begins to crack...",
                "An ancient prophecy foretells..."
            },
            challenges = {
                {type = "grammar", difficulty = 1, topic = "Subject-Verb Agreement"},
                {type = "vocabulary", difficulty = 2, topic = "Fantasy Terms"},
                {type = "creative", difficulty = 2, topic = "Character Description"}
            }
        },
        scifi = {
            name = "Galactic Federation",
            elements = {"spaceships", "aliens", "technology", "exploration"},
            writingPrompts = {
                "The starship crew encounters a strange signal...",
                "A new planet appears on the scanner...",
                "The AI begins to show signs of consciousness..."
            },
            challenges = {
                {type = "grammar", difficulty = 2, topic = "Complex Sentences"},
                {type = "vocabulary", difficulty = 3, topic = "Scientific Terms"},
                {type = "creative", difficulty = 2, topic = "Setting Description"}
            }
        },
        mystery = {
            name = "Detective Chronicles",
            elements = {"clues", "suspects", "investigation", "secrets"},
            writingPrompts = {
                "The detective finds a mysterious letter...",
                "A witness comes forward with new information...",
                "The case takes an unexpected turn..."
            },
            challenges = {
                {type = "grammar", difficulty = 2, topic = "Dialogue Punctuation"},
                {type = "vocabulary", difficulty = 2, topic = "Detective Jargon"},
                {type = "creative", difficulty = 3, topic = "Plot Twist Creation"}
            }
        }
    }
end

-- Initialize grammar enemies
function StoryForgeAdventure:initializeGrammarEnemies()
    self.grammarEnemies = {
        ["Comma Splice Monster"] = {
            rule = "Comma Splices",
            challenge = "Fix this sentence: The dog ran fast it was chasing a ball.",
            correctAnswer = "The dog ran fast; it was chasing a ball.",
            difficulty = 1
        },
        ["Dangling Modifier Beast"] = {
            rule = "Dangling Modifiers",
            challenge = "Fix: Walking through the park, the flowers were beautiful.",
            correctAnswer = "Walking through the park, I saw beautiful flowers.",
            difficulty = 2
        },
        ["Tense Confusion Troll"] = {
            rule = "Verb Tense Consistency",
            challenge = "Fix: Yesterday, I go to the store and buy milk.",
            correctAnswer = "Yesterday, I went to the store and bought milk.",
            difficulty = 1
        }
    }
end

-- Setup event handlers
function StoryForgeAdventure:setupEventHandlers()
    self.remotes.EnterWorld.OnServerEvent:Connect(function(player, worldKey)
        self:enterWorld(player, worldKey)
    end)
    
    self.remotes.CompleteChallenge.OnServerEvent:Connect(function(player, challengeType)
        self:completeChallenge(player, challengeType)
    end)
    
    self.remotes.GrammarBattle.OnServerEvent:Connect(function(player, enemyName, answer)
        self:grammarBattle(player, enemyName, answer)
    end)
    
    self.remotes.CreateCharacter.OnServerEvent:Connect(function(player, characterData)
        self:createCharacter(player, characterData)
    end)
    
    self.remotes.WriteStory.OnServerEvent:Connect(function(player, storyText)
        self:writeStory(player, storyText)
    end)
    
    self.remotes.CreatePoem.OnServerEvent:Connect(function(player, poemType, poemText)
        self:createPoem(player, poemType, poemText)
    end)
    
    Players.PlayerAdded:Connect(function(player)
        self:initializePlayerData(player)
    end)
end

-- Initialize player data
function StoryForgeAdventure:initializePlayerData(player)
    self.playerData[player.UserId] = {
        currentWorld = nil,
        writingSkills = {
            grammar = 1,
            vocabulary = 1,
            creativity = 1,
            structure = 1
        },
        completedStories = {},
        characterJournal = {},
        writingTools = {},
        experience = 0
    }
end

-- Enter story world
function StoryForgeAdventure:enterWorld(player, worldKey)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    local world = self.storyWorlds[worldKey]
    
    if world then
        playerData.currentWorld = worldKey
        
        -- Create world environment
        self:createWorldEnvironment(worldKey)
        
        self.remotes.EnterWorld:FireClient(player, {
            success = true,
            world = world
        })
    end
end

-- Create world environment
function StoryForgeAdventure:createWorldEnvironment(worldKey)
    -- Clear existing environment
    for _, obj in ipairs(workspace:GetChildren()) do
        if obj:FindFirstChild("StoryWorld") then
            obj:Destroy()
        end
    end
    
    local world = self.storyWorlds[worldKey]
    local environment = Instance.new("Model")
    environment.Name = world.name .. "_Environment"
    
    local tag = Instance.new("BoolValue")
    tag.Name = "StoryWorld"
    tag.Parent = environment
    
    -- Create themed environment
    if worldKey == "fantasy" then
        -- Create castle
        local castle = Instance.new("Part")
        castle.Name = "Castle"
        castle.Size = Vector3.new(50, 50, 50)
        castle.Position = Vector3.new(0, 25, 0)
        castle.Anchored = true
        castle.BrickColor = BrickColor.new("Medium stone grey")
        castle.Parent = environment
        
    elseif worldKey == "scifi" then
        -- Create spaceship
        local ship = Instance.new("Part")
        ship.Name = "Spaceship"
        ship.Size = Vector3.new(30, 15, 60)
        ship.Position = Vector3.new(0, 10, 0)
        ship.Anchored = true
        ship.BrickColor = BrickColor.new("Silver")
        ship.Parent = environment
        
    elseif worldKey == "mystery" then
        -- Create detective office
        local office = Instance.new("Part")
        office.Name = "DetectiveOffice"
        office.Size = Vector3.new(20, 12, 20)
        office.Position = Vector3.new(0, 6, 0)
        office.Anchored = true
        office.BrickColor = BrickColor.new("Brown")
        office.Parent = environment
    end
    
    environment.Parent = workspace
end

-- Complete writing challenge
function StoryForgeAdventure:completeChallenge(player, challengeType)
    local playerData = self.playerData[player.UserId]
    
    if not playerData or not playerData.currentWorld then
        return
    end
    
    local challenges = {
        grammar = {
            description = "Fix the grammatical errors",
            xpReward = 20
        },
        vocabulary = {
            description = "Find synonyms and antonyms",
            xpReward = 25
        },
        creative = {
            description = "Create an original story element",
            xpReward = 30
        }
    }
    
    local challenge = challenges[challengeType]
    
    if challenge then
        -- Simulate challenge completion
        playerData.experience = playerData.experience + challenge.xpReward
        
        -- Improve skill
        if playerData.writingSkills[challengeType] then
            playerData.writingSkills[challengeType] = playerData.writingSkills[challengeType] + 1
        end
        
        self.remotes.CompleteChallenge:FireClient(player, {
            success = true,
            xpReward = challenge.xpReward
        })
    end
end

-- Grammar battle
function StoryForgeAdventure:grammarBattle(player, enemyName, answer)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    local enemy = self.grammarEnemies[enemyName]
    
    if enemy then
        if answer == enemy.correctAnswer then
            -- Victory
            playerData.experience = playerData.experience + (20 * enemy.difficulty)
            playerData.writingSkills.grammar = playerData.writingSkills.grammar + 1
            
            self.remotes.GrammarBattle:FireClient(player, {
                success = true,
                victory = true,
                xpReward = 20 * enemy.difficulty
            })
        else
            -- Defeat
            self.remotes.GrammarBattle:FireClient(player, {
                success = true,
                victory = false,
                correctAnswer = enemy.correctAnswer
            })
        end
    end
end

-- Create character
function StoryForgeAdventure:createCharacter(player, characterData)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    table.insert(playerData.characterJournal, {
        name = characterData.name,
        traits = characterData.traits,
        backstory = characterData.backstory or "",
        relationships = {}
    })
    
    playerData.writingSkills.creativity = playerData.writingSkills.creativity + 1
    playerData.experience = playerData.experience + 15
    
    self.remotes.CreateCharacter:FireClient(player, {
        success = true,
        xpReward = 15
    })
end

-- Write story
function StoryForgeAdventure:writeStory(player, storyText)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    table.insert(playerData.completedStories, {
        text = storyText,
        worldType = playerData.currentWorld,
        timestamp = os.time()
    })
    
    -- Analyze story for writing elements
    local wordCount = #string.split(storyText, " ")
    local xpReward = math.min(wordCount * 0.1, 50)
    
    playerData.experience = playerData.experience + xpReward
    playerData.writingSkills.structure = playerData.writingSkills.structure + 1
    
    self.remotes.WriteStory:FireClient(player, {
        success = true,
        xpReward = xpReward
    })
end

-- Create poem
function StoryForgeAdventure:createPoem(player, poemType, poemText)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    local poemTypes = {
        haiku = {structure = "5-7-5 syllables", xpReward = 25},
        limerick = {structure = "AABBA rhyme scheme", xpReward = 30},
        freeverse = {structure = "No set structure", xpReward = 20}
    }
    
    local poem = poemTypes[poemType]
    
    if poem then
        playerData.experience = playerData.experience + poem.xpReward
        playerData.writingSkills.creativity = playerData.writingSkills.creativity + 1
        
        self.remotes.CreatePoem:FireClient(player, {
            success = true,
            xpReward = poem.xpReward
        })
    end
end

-- Create and return the game instance
return StoryForgeAdventure.new()