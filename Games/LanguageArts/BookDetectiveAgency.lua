-- Book Detective Agency Script
-- Place this in ServerScriptService

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

-- Create the main game module
local BookDetectiveAgency = {}
BookDetectiveAgency.__index = BookDetectiveAgency

function BookDetectiveAgency.new()
    local self = setmetatable({}, BookDetectiveAgency)
    
    self.cases = {}
    self.playerData = {}
    self.library = {}
    
    -- Create remote events
    self.remotes = {
        StartCase = Instance.new("RemoteEvent"),
        SearchForClues = Instance.new("RemoteEvent"),
        InterviewSuspect = Instance.new("RemoteEvent"),
        AnalyzeText = Instance.new("RemoteEvent"),
        SolveCase = Instance.new("RemoteEvent"),
        ExploreLibrary = Instance.new("RemoteEvent")
    }
    
    for name, remote in pairs(self.remotes) do
        remote.Name = name
        remote.Parent = ReplicatedStorage
    end
    
    self:initializeCases()
    self:initializeLibrary()
    self:setupEventHandlers()
    
    return self
end

-- Initialize cases
function BookDetectiveAgency:initializeCases()
    self.cases = {
        mystery_mansion = {
            title = "The Mystery of the Vanishing Manuscript",
            description = "A valuable manuscript has disappeared from the author's study",
            clues = {
                {text = "A torn page near the window", importance = 3, location = "Study"},
                {text = "Ink stains on the carpet", importance = 2, location = "Library"},
                {text = "A bookmark with cryptic notes", importance = 5, location = "Office"},
                {text = "Muddy footprints leading away", importance = 4, location = "Hallway"}
            },
            suspects = {
                {name = "Butler", motive = "Financial gain", alibi = "Was serving dinner"},
                {name = "Author", motive = "Insurance fraud", alibi = "Working in garden"},
                {name = "Publisher", motive = "Deadline pressure", alibi = "At meeting"}
            },
            solution = "Author hid the manuscript for publicity"
        },
        literary_theft = {
            title = "The Case of the Stolen Story",
            description = "Similar stories appear in two different books",
            clues = {
                {text = "Similar plot elements", importance = 4, location = "Book 1"},
                {text = "Matching character names", importance = 5, location = "Book 2"},
                {text = "Publication date discrepancy", importance = 3, location = "Records"},
                {text = "Writing style analysis", importance = 4, location = "Analysis"}
            },
            suspects = {
                {name = "Rival Writer", motive = "Fame", alibi = "On book tour"},
                {name = "Editor", motive = "Double profit", alibi = "Editing other work"},
                {name = "Ghost Writer", motive = "Recognition", alibi = "No record"}
            },
            solution = "Ghost Writer published work independently"
        }
    }
end

-- Initialize library
function BookDetectiveAgency:initializeLibrary()
    self.library = {
        reference = {
            {title = "Detective's Handbook", skill = "comprehension", xpReward = 15},
            {title = "Literary Analysis Guide", skill = "analysis", xpReward = 20},
            {title = "Art of Deduction", skill = "deduction", xpReward = 25}
        },
        fiction = {
            {title = "Mystery Collection", skill = "inference", xpReward = 10},
            {title = "Classic Detective Stories", skill = "comprehension", xpReward = 15}
        }
    }
end

-- Setup event handlers
function BookDetectiveAgency:setupEventHandlers()
    self.remotes.StartCase.OnServerEvent:Connect(function(player, caseKey)
        self:startCase(player, caseKey)
    end)
    
    self.remotes.SearchForClues.OnServerEvent:Connect(function(player, location)
        self:searchForClues(player, location)
    end)
    
    self.remotes.InterviewSuspect.OnServerEvent:Connect(function(player, suspectName)
        self:interviewSuspect(player, suspectName)
    end)
    
    self.remotes.AnalyzeText.OnServerEvent:Connect(function(player, textType)
        self:analyzeText(player, textType)
    end)
    
    self.remotes.SolveCase.OnServerEvent:Connect(function(player, solution)
        self:solveCase(player, solution)
    end)
    
    self.remotes.ExploreLibrary.OnServerEvent:Connect(function(player)
        self:exploreLibrary(player)
    end)
    
    Players.PlayerAdded:Connect(function(player)
        self:initializePlayerData(player)
    end)
end

-- Initialize player data
function BookDetectiveAgency:initializePlayerData(player)
    self.playerData[player.UserId] = {
        currentCase = nil,
        discoveredClues = {},
        interviewedSuspects = {},
        solvedCases = {},
        detectionSkills = {
            comprehension = 1,
            analysis = 1,
            inference = 1,
            deduction = 1
        },
        libraryBooks = {},
        experience = 0
    }
end

-- Start case
function BookDetectiveAgency:startCase(player, caseKey)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    local case = self.cases[caseKey]
    
    if case then
        playerData.currentCase = caseKey
        playerData.discoveredClues = {}
        playerData.interviewedSuspects = {}
        
        -- Create case environment
        self:createCaseEnvironment(caseKey)
        
        self.remotes.StartCase:FireClient(player, {
            success = true,
            case = case
        })
    end
end

-- Create case environment
function BookDetectiveAgency:createCaseEnvironment(caseKey)
    -- Clear existing environment
    for _, obj in ipairs(workspace:GetChildren()) do
        if obj:FindFirstChild("DetectiveCase") then
            obj:Destroy()
        end
    end
    
    local case = self.cases[caseKey]
    local environment = Instance.new("Model")
    environment.Name = case.title .. "_Environment"
    
    local tag = Instance.new("BoolValue")
    tag.Name = "DetectiveCase"
    tag.Parent = environment
    
    -- Create detective office
    local office = Instance.new("Part")
    office.Name = "DetectiveOffice"
    office.Size = Vector3.new(20, 12, 20)
    office.Position = Vector3.new(0, 6, 0)
    office.Anchored = true
    office.BrickColor = BrickColor.new("Brown")
    office.Parent = environment
    
    -- Create investigation locations
    local locations = {"Study", "Library", "Office", "Hallway"}
    
    for i, location in ipairs(locations) do
        local part = Instance.new("Part")
        part.Name = location
        part.Size = Vector3.new(15, 10, 15)
        part.Position = Vector3.new(i * 20 - 40, 5, 20)
        part.Anchored = true
        part.Parent = environment
        
        -- Add interaction
        local clickDetector = Instance.new("ClickDetector")
        clickDetector.Parent = part
        
        clickDetector.MouseClick:Connect(function(player)
            self:searchForClues(player, location)
        end)
        
        -- Add label
        local billboard = Instance.new("BillboardGui")
        billboard.Size = UDim2.new(0, 200, 0, 50)
        billboard.StudsOffset = Vector3.new(0, 8, 0)
        billboard.Parent = part
        
        local label = Instance.new("TextLabel")
        label.Size = UDim2.new(1, 0, 1, 0)
        label.Text = location
        label.TextScaled = true
        label.BackgroundTransparency = 1
        label.Parent = billboard
    end
    
    environment.Parent = workspace
end

-- Search for clues
function BookDetectiveAgency:searchForClues(player, location)
    local playerData = self.playerData[player.UserId]
    
    if not playerData or not playerData.currentCase then
        return
    end
    
    local case = self.cases[playerData.currentCase]
    
    -- Find clues in this location
    for _, clue in ipairs(case.clues) do
        if clue.location == location and not self:hasDiscoveredClue(playerData, clue) then
            table.insert(playerData.discoveredClues, clue)
            
            -- Improve skills
            playerData.detectionSkills.comprehension = playerData.detectionSkills.comprehension + 
                (clue.importance * 0.5)
            
            playerData.experience = playerData.experience + (clue.importance * 5)
            
            self.remotes.SearchForClues:FireClient(player, {
                success = true,
                clue = clue
            })
            
            return
        end
    end
    
    self.remotes.SearchForClues:FireClient(player, {
        success = false,
        message = "No new clues found here."
    })
end

-- Has discovered clue
function BookDetectiveAgency:hasDiscoveredClue(playerData, clue)
    for _, discoveredClue in ipairs(playerData.discoveredClues) do
        if discoveredClue.text == clue.text then
            return true
        end
    end
    return false
end

-- Interview suspect
function BookDetectiveAgency:interviewSuspect(player, suspectName)
    local playerData = self.playerData[player.UserId]
    
    if not playerData or not playerData.currentCase then
        return
    end
    
    local case = self.cases[playerData.currentCase]
    
    for _, suspect in ipairs(case.suspects) do
        if suspect.name == suspectName then
            table.insert(playerData.interviewedSuspects, suspect)
            
            -- Improve skills
            playerData.detectionSkills.analysis = playerData.detectionSkills.analysis + 1
            playerData.experience = playerData.experience + 20
            
            self.remotes.InterviewSuspect:FireClient(player, {
                success = true,
                suspect = suspect
            })
            
            return
        end
    end
end

-- Analyze text
function BookDetectiveAgency:analyzeText(player, textType)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    local analysisTypes = {
        character = {skill = "analysis", xpReward = 15},
        plot = {skill = "inference", xpReward = 20},
        theme = {skill = "comprehension", xpReward = 25},
        style = {skill = "analysis", xpReward = 15}
    }
    
    local analysis = analysisTypes[textType]
    
    if analysis then
        playerData.detectionSkills[analysis.skill] = playerData.detectionSkills[analysis.skill] + 1
        playerData.experience = playerData.experience + analysis.xpReward
        
        self.remotes.AnalyzeText:FireClient(player, {
            success = true,
            analysis = analysis
        })
    end
end

-- Solve case
function BookDetectiveAgency:solveCase(player, solution)
    local playerData = self.playerData[player.UserId]
    
    if not playerData or not playerData.currentCase then
        return
    end
    
    local case = self.cases[playerData.currentCase]
    
    if solution == case.solution then
        -- Case solved correctly
        table.insert(playerData.solvedCases, {
            title = case.title,
            solution = solution,
            cluesFound = #playerData.discoveredClues
        })
        
        playerData.detectionSkills.deduction = playerData.detectionSkills.deduction + 5
        playerData.experience = playerData.experience + 100
        
        self.remotes.SolveCase:FireClient(player, {
            success = true,
            correct = true,
            xpReward = 100
        })
    else
        self.remotes.SolveCase:FireClient(player, {
            success = true,
            correct = false,
            message = "That's not the correct solution. Keep investigating!"
        })
    end
end

-- Explore library
function BookDetectiveAgency:exploreLibrary(player)
    local playerData = self.playerData[player.UserId]
    
    if not playerData then
        return
    end
    
    -- Find random book
    local sections = {"reference", "fiction"}
    local section = sections[math.random(#sections)]
    local books = self.library[section]
    local book = books[math.random(#books)]
    
    -- Add to player's collection
    table.insert(playerData.libraryBooks, book)
    
    -- Improve skill
    playerData.detectionSkills[book.skill] = playerData.detectionSkills[book.skill] + 1
    playerData.experience = playerData.experience + book.xpReward
    
    self.remotes.ExploreLibrary:FireClient(player, {
        success = true,
        book = book
    })
end

-- Create and return the game instance
return BookDetectiveAgency.new()