-- Math Quest Arena Script
-- Place this in ServerScriptService

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

-- Create the main game module
local MathQuestArena = {}
MathQuestArena.__index = MathQuestArena

-- Initialize game state
function MathQuestArena.new()
    local self = setmetatable({}, MathQuestArena)
    
    self.dungeons = {}
    self.currentPlayers = {}
    self.problems = {}
    
    -- Create remote events for client-server communication
    self.remotes = {
        StartDungeon = Instance.new("RemoteEvent"),
        SubmitAnswer = Instance.new("RemoteEvent"),
        UpdateProgress = Instance.new("RemoteEvent"),
        BattleResult = Instance.new("RemoteEvent")
    }
    
    for name, remote in pairs(self.remotes) do
        remote.Name = name
        remote.Parent = ReplicatedStorage
    end
    
    self:initializeDungeons()
    self:setupEventHandlers()
    
    return self
end

-- Initialize dungeons from configuration
function MathQuestArena:initializeDungeons()
    self.dungeons = {
        -- Default dungeons
        arithmetic = {
            name = "Arithmetic Caverns",
            difficulty = 1,
            monsters = {"Addition Goblin", "Subtraction Troll", "Multiplication Mage"},
            boss = "Division Dragon",
            topics = {"addition", "subtraction", "multiplication", "division"}
        },
        
        -- [INJECT_DUNGEONS]
    }
end

-- Setup event handlers
function MathQuestArena:setupEventHandlers()
    -- Handle player joining dungeon
    self.remotes.StartDungeon.OnServerEvent:Connect(function(player, dungeonName)
        self:startDungeon(player, dungeonName)
    end)
    
    -- Handle answer submission
    self.remotes.SubmitAnswer.OnServerEvent:Connect(function(player, answer)
        self:processAnswer(player, answer)
    end)
end

-- Start dungeon for player
function MathQuestArena:startDungeon(player, dungeonName)
    local dungeon = self.dungeons[dungeonName]
    
    if not dungeon then
        return
    end
    
    local playerData = {
        currentDungeon = dungeonName,
        level = 1,
        health = 100,
        xp = 0,
        currentMonster = 1,
        currentProblem = nil
    }
    
    self.currentPlayers[player.UserId] = playerData
    
    -- Generate first problem
    local problem = self:generateProblem(dungeon.topics[1], dungeon.difficulty)
    playerData.currentProblem = problem
    
    -- Send problem to client
    self.remotes.UpdateProgress:FireClient(player, {
        dungeon = dungeonName,
        monster = dungeon.monsters[1],
        problem = problem
    })
end

-- Generate math problem based on topic and difficulty
function MathQuestArena:generateProblem(topic, difficulty)
    -- [INJECT_PROBLEMS]
    
    if topic == "addition" then
        local a = math.random(1, 10 * difficulty)
        local b = math.random(1, 10 * difficulty)
        return {
            question = a .. " + " .. b .. " = ?",
            answer = a + b,
            topic = topic
        }
    elseif topic == "subtraction" then
        local a = math.random(1, 10 * difficulty)
        local b = math.random(1, a)
        return {
            question = a .. " - " .. b .. " = ?",
            answer = a - b,
            topic = topic
        }
    elseif topic == "multiplication" then
        local a = math.random(1, 5 * difficulty)
        local b = math.random(1, 5 * difficulty)
        return {
            question = a .. " × " .. b .. " = ?",
            answer = a * b,
            topic = topic
        }
    elseif topic == "division" then
        local b = math.random(1, 5 * difficulty)
        local answer = math.random(1, 5 * difficulty)
        local a = b * answer
        return {
            question = a .. " ÷ " .. b .. " = ?",
            answer = answer,
            topic = topic
        }
    end
    
    -- Default problem
    return {
        question = "1 + 1 = ?",
        answer = 2,
        topic = "addition"
    }
end

-- Process player's answer
function MathQuestArena:processAnswer(player, answer)
    local playerData = self.currentPlayers[player.UserId]
    
    if not playerData or not playerData.currentProblem then
        return
    end
    
    local correct = answer == playerData.currentProblem.answer
    local dungeon = self.dungeons[playerData.currentDungeon]
    
    if correct then
        -- Reward player
        playerData.xp = playerData.xp + (10 * dungeon.difficulty)
        
        -- Check for level up
        if playerData.xp >= playerData.level * 100 then
            playerData.level = playerData.level + 1
        end
        
        -- Progress to next monster or boss
        playerData.currentMonster = playerData.currentMonster + 1
        
        if playerData.currentMonster > #dungeon.monsters then
            -- Boss battle
            self:startBossBattle(player, playerData)
        else
            -- Next monster
            local problem = self:generateProblem(
                dungeon.topics[math.min(playerData.currentMonster, #dungeon.topics)],
                dungeon.difficulty
            )
            playerData.currentProblem = problem
            
            self.remotes.UpdateProgress:FireClient(player, {
                monster = dungeon.monsters[playerData.currentMonster],
                problem = problem,
                xp = playerData.xp,
                level = playerData.level
            })
        end
    else
        -- Player takes damage
        playerData.health = playerData.health - 10
        
        if playerData.health <= 0 then
            -- Game over
            self:endDungeon(player, false)
        else
            self.remotes.BattleResult:FireClient(player, {
                correct = false,
                health = playerData.health,
                message = "Incorrect! The monster attacks!"
            })
        end
    end
    
    self.remotes.BattleResult:FireClient(player, {
        correct = correct,
        xp = playerData.xp,
        level = playerData.level,
        health = playerData.health
    })
end

-- Start boss battle
function MathQuestArena:startBossBattle(player, playerData)
    local dungeon = self.dungeons[playerData.currentDungeon]
    
    -- Generate boss problem (more difficult)
    local problem = self:generateProblem(
        dungeon.topics[#dungeon.topics],
        dungeon.difficulty * 2
    )
    
    playerData.currentProblem = problem
    
    self.remotes.UpdateProgress:FireClient(player, {
        monster = dungeon.boss,
        problem = problem,
        isBoss = true
    })
end

-- End dungeon
function MathQuestArena:endDungeon(player, victory)
    local playerData = self.currentPlayers[player.UserId]
    
    if not playerData then
        return
    end
    
    if victory then
        -- Award completion bonus
        playerData.xp = playerData.xp + 100
    end
    
    self.remotes.UpdateProgress:FireClient(player, {
        dungeonComplete = true,
        victory = victory,
        finalXP = playerData.xp,
        finalLevel = playerData.level
    })
    
    -- Clean up player data
    self.currentPlayers[player.UserId] = nil
end

-- Create and return the game instance
return MathQuestArena.new()