-- Number Parkour Challenge Script
-- Place this in ServerScriptService

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

-- Create the main game module
local NumberParkour = {}
NumberParkour.__index = NumberParkour

function NumberParkour.new()
    local self = setmetatable({}, NumberParkour)
    
    self.platforms = {}
    self.playerData = {}
    self.leaderboard = {}
    self.currentLevel = 1
    
    -- Create remote events
    self.remotes = {
        StartGame = Instance.new("RemoteEvent"),
        PlatformLanded = Instance.new("RemoteEvent"),
        LevelComplete = Instance.new("RemoteEvent"),
        UpdateLeaderboard = Instance.new("RemoteEvent")
    }
    
    for name, remote in pairs(self.remotes) do
        remote.Name = name
        remote.Parent = ReplicatedStorage
    end
    
    self:setupEventHandlers()
    
    return self
end

-- Setup event handlers
function NumberParkour:setupEventHandlers()
    self.remotes.StartGame.OnServerEvent:Connect(function(player)
        self:startGameForPlayer(player)
    end)
    
    self.remotes.PlatformLanded.OnServerEvent:Connect(function(player, platformId)
        self:handlePlatformLanding(player, platformId)
    end)
    
    Players.PlayerRemoving:Connect(function(player)
        self.playerData[player.UserId] = nil
    end)
end

-- Start game for player
function NumberParkour:startGameForPlayer(player)
    self.playerData[player.UserId] = {
        level = 1,
        score = 0,
        startTime = tick(),
        attempts = 0
    }
    
    self:generatePlatforms(1)
    self:spawnPlayerAtStart(player)
end

-- Generate platforms with math problems
function NumberParkour:generatePlatforms(level)
    self.platforms = {}
    
    -- Create platforms in a parkour course layout
    for i = 1, 10 + (level * 2) do
        local platform = {
            id = i,
            position = Vector3.new(
                i * 10,
                5 + math.sin(i / 3) * 5, -- Varying heights
                math.cos(i / 2) * 5 -- Zigzag pattern
            ),
            problem = self:generateMathProblem(level),
            isCorrect = false
        }
        
        -- Create physical platform
        local part = Instance.new("Part")
        part.Name = "Platform_" .. i
        part.Size = Vector3.new(8, 1, 8)
        part.Position = platform.position
        part.Anchored = true
        part.Parent = workspace
        
        -- Add visual indicator for math problem
        local billboard = Instance.new("BillboardGui")
        billboard.Size = UDim2.new(0, 200, 0, 50)
        billboard.StudsOffset = Vector3.new(0, 3, 0)
        billboard.Parent = part
        
        local textLabel = Instance.new("TextLabel")
        textLabel.Size = UDim2.new(1, 0, 1, 0)
        textLabel.Text = platform.problem.equation
        textLabel.TextScaled = true
        textLabel.BackgroundTransparency = 1
        textLabel.Parent = billboard
        
        -- Add touch detector
        local detector = Instance.new("Part")
        detector.Name = "Detector"
        detector.Size = part.Size + Vector3.new(0, 2, 0)
        detector.Position = part.Position + Vector3.new(0, 1, 0)
        detector.Transparency = 1
        detector.CanCollide = false
        detector.Parent = part
        
        detector.Touched:Connect(function(hit)
            local character = hit.Parent
            local player = Players:GetPlayerFromCharacter(character)
            
            if player then
                self:handlePlatformLanding(player, i)
            end
        end)
        
        table.insert(self.platforms, platform)
    end
    
    -- Set one platform as correct answer
    local correctIndex = math.random(1, #self.platforms)
    self.platforms[correctIndex].isCorrect = true
    
    -- Color correct platform green (for testing)
    workspace["Platform_" .. correctIndex].BrickColor = BrickColor.new("Bright green")
end

-- Generate math problem based on level
function NumberParkour:generateMathProblem(level)
    local operations = {"+", "-", "*"}
    local operation = operations[math.min(level, #operations)]
    
    local num1 = math.random(1, 10 * level)
    local num2 = math.random(1, 10 * level)
    
    if operation == "-" then
        -- Ensure positive result
        num1 = math.max(num1, num2)
    end
    
    local answer
    if operation == "+" then
        answer = num1 + num2
    elseif operation == "-" then
        answer = num1 - num2
    elseif operation == "*" then
        answer = num1 * num2
    end
    
    return {
        equation = num1 .. " " .. operation .. " " .. num2,
        answer = answer
    }
end

-- Handle platform landing
function NumberParkour:handlePlatformLanding(player, platformId)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    local platform = self.platforms[platformId]
    
    if platform.isCorrect then
        -- Correct platform
        playerData.score = playerData.score + (100 * playerData.level)
        playerData.level = playerData.level + 1
        
        -- Clear old platforms
        for _, platformInstance in ipairs(workspace:GetChildren()) do
            if platformInstance.Name:match("^Platform_") then
                platformInstance:Destroy()
            end
        end
        
        -- Generate new level
        self:generatePlatforms(playerData.level)
        
        self.remotes.LevelComplete:FireClient(player, {
            level = playerData.level,
            score = playerData.score
        })
    else
        -- Wrong platform - respawn player
        playerData.attempts = playerData.attempts + 1
        self:spawnPlayerAtStart(player)
    end
end

-- Spawn player at start position
function NumberParkour:spawnPlayerAtStart(player)
    local character = player.Character
    
    if character then
        local humanoidRootPart = character:FindFirstChild("HumanoidRootPart")
        
        if humanoidRootPart then
            humanoidRootPart.CFrame = CFrame.new(0, 10, 0)
        end
    end
end

-- Update leaderboard
function NumberParkour:updateLeaderboard(player, score)
    table.insert(self.leaderboard, {
        playerName = player.Name,
        score = score,
        time = tick() - self.playerData[player.UserId].startTime
    })
    
    -- Sort leaderboard by score
    table.sort(self.leaderboard, function(a, b)
        return a.score > b.score
    end)
    
    -- Keep only top 10
    while #self.leaderboard > 10 do
        table.remove(self.leaderboard)
    end
    
    -- Update all clients
    for _, player in ipairs(Players:GetPlayers()) do
        self.remotes.UpdateLeaderboard:FireClient(player, self.leaderboard)
    end
end

-- Create and return the game instance
return NumberParkour.new()