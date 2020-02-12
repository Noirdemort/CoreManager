import Foundation

// MARK:- Interface Handler

func consoleInput(annotation: String, required: Bool = true, secureInput: Bool = false) -> String {
    print(annotation)
    
    var input: String
    
    if secureInput {
        
        var buf = [CChar](repeating: 0, count: 8192)
        guard let passphrase = readpassphrase("Enter secure input: ", &buf, buf.count, 0) else {
            print("[!] Pointer error")
            exit(EXIT_FAILURE)
        }
        input = String(validatingUTF8: passphrase) ?? ""
        
    } else {
        
        input = readLine(strippingNewline: true) ?? ""
        
    }
    
    if required && input.isEmpty {
        print("[!] Input Error")
        exit(EXIT_FAILURE)
    }
    
    
    return input
    
}

extension String {
    func engageSecure() -> String?{
        if self.isEmpty {
            return nil
        }
        return self
    }
}

// MARK:- FileIO


protocol JSONOperator {
    static func readJSON<T: CoreAccount>() throws -> [T]
    static func saveJSON<T: CoreAccount>(data: [T]) throws
}


struct JSOC: JSONOperator {
    
    static let fileManager = FileManager()
    static let home = fileManager.homeDirectoryForCurrentUser.absoluteString
    static let file = "blackburn.json"
    
    static func readJSON<T: Decodable>() throws -> [T] {
        
        let data = fileManager.contents(atPath: home + file)
        
        let decoder = JSONDecoder()
        
        return try decoder.decode([T].self, from: data!)
        
    }
    
    static func saveJSON<T: Encodable>(data: [T]) throws {
        let encoder = JSONEncoder()
        let data = try encoder.encode(data)
        
        if fileManager.fileExists(atPath: home + file){
            try fileManager.removeItem(atPath: home + file)
        }
        
        fileManager.createFile(atPath: home + file, contents: data, attributes: nil)
    }
    
}


// MARK:- Account Handler

protocol Security {
    func encrypt()
    static func sha(text: String) -> String
    func decrypt()
    static func saltGenerator(length: Int) -> String
}

protocol CoreAccount: Codable, Equatable, Security {
    var username: String { get set }
    var password: String { get set }
    var email: String { get set }
    var salt: String { get set }
    var projects: [Project] { get set }
    
    static func newAccount() -> Self
    static func login() -> Self?
    static func loadAccount(username: String, email: String?) -> Self
    func exportAccount(encrypted: Bool)
    static func readAccounts() -> [Self]
    static func verify(username: String, currentKey: String) -> Self?
    func signOut()
}


struct Account: CoreAccount {
    
    var username: String
    
    var password: String
    
    var email: String
    
    var salt: String
    
    var projects: [Project] = []

    
    static func newAccount() -> Account {
        let username = consoleInput(annotation: "Enter Username: ")
        
        let password = consoleInput(annotation: "Secure key: ", secureInput: true)
        
        let confirmedPassword = consoleInput(annotation: "Confirm Key: ", secureInput: true)
        
        if confirmedPassword != password {
            print("[!] Passwords mismatch.")
            exit(EXIT_FAILURE)
        }
        
        let email = consoleInput(annotation: "Enter email: ")
        
        let salt = saltGenerator()
        
        return Account(username: username, password: password, email: email, salt: salt)
    }
    
    
    static func login() -> Account? {
        print("[*] Login Terminal")
        let username = consoleInput(annotation: "Enter Username: ")
        let password = consoleInput(annotation: "Secure key: ", secureInput: true)
        
        if var account = verify(username: username, currentKey: password) {
            print("[+] Login Successful!!")
            account.password = password
            return account
        }
        
        print("[!] Invalid Credentials")
        exit(EXIT_FAILURE)
    }
    
    
    static func verify(username: String, currentKey: String) -> Account? {
        let account = loadAccount(username: username, email: nil)
        if sha(text: currentKey + account.salt) == account.password {
            return account
        }
        
        return nil
    }
    
    static func loadAccount(username: String, email: String?) -> Account {
        let accounts = readAccounts()
        guard let account =  accounts.first(where: { $0.username == username}) else {
            print("[!] No such account!!")
            exit(EXIT_FAILURE)
        }
        
        return account
    }
    
    static func readAccounts() -> [Account] {
        do {
            let accounts: [Account] = try JSOC.readJSON()
            return accounts
        } catch {
            print(error.localizedDescription)
            exit(EXIT_FAILURE)
        }
    }
    
    func exportAccount(encrypted: Bool) {
        do {
            var accounts = Account.readAccounts()
            if !accounts.contains(self){
                accounts.append(self)
            }
            try JSOC.saveJSON(data: accounts)
        } catch {
            print(error.localizedDescription)
            exit(EXIT_FAILURE)
        }
    }
    
    func signOut() {
        exit(EXIT_SUCCESS)
    }
    
    
    func encrypt() {
        
    }
    
    
    static func sha(text: String) -> String {
        // TODO:- Start using sodium here
        return "brackish4953219water"
    }
    
    
    func decrypt() {
        
    }
    
    
    static func saltGenerator(length: Int = 10) -> String {
        return UUID().uuidString
    }
}


// MARK:- Project Handler


protocol CoreProject: Codable, Equatable {
    
    var id: String { get set }
    var name: String { get set }
    var category: String? { get set }
    var tags: String? { get set }
    var description: String { get set }
    var createdBy: String { get }
    var tasks: [Task] { get set }
    
    static func createNewProject(account: inout Account) -> Self
    static func loadProject(account: Account) -> Self?
    func addFiles() throws
    func modifyProject()
    func deleteProject()
    func exportProject()
    
}


struct Project: CoreProject {
    static func == (lhs: Project, rhs: Project) -> Bool {
        return lhs.id == rhs.id && lhs.name == rhs.name && lhs.createdBy == rhs.createdBy
    }
    
    var id: String
    
    var name: String
    
    var category: String?
    
    var tags: String?
    
    var description: String
    
    var createdBy: String
    
    var tasks: [Task] = []
    
    
    static func createNewProject( account: inout Account) -> Project {
        var id = consoleInput(annotation: "Enter project id (Optional): ", required: false, secureInput: false)
        if id.isEmpty {
            id = UUID().uuidString
        }
        let name = consoleInput(annotation: "Enter project name: ")
        let description = consoleInput(annotation: "Enter project description: ")
        let category = consoleInput(annotation: "Enter project category (Optional): ", required: false).engageSecure()
        let tags = consoleInput(annotation: "Enter project tags (Optional): ", required: false).engageSecure()
        let project = Project(id: id, name: name, category: category, tags: tags, description: description, createdBy: account.username)
        account.projects.append(project)
        return project
    }
    
    static func loadProject(account: Account) -> Project? {
        let name = consoleInput(annotation: "Enter project name: ")
        do {
            let projects: [Project] = try JSOC.readJSON()
            let selection = projects.filter({ $0.createdBy == account.username && $0.name == name })
            return selection.first
        } catch {
            print(error.localizedDescription)
            exit(EXIT_FAILURE)
        }
    }
    
    static func readProjects() -> [Project] {
        do {
            let accounts: [Project] = try JSOC.readJSON()
            return accounts
        } catch {
            print(error.localizedDescription)
            exit(EXIT_FAILURE)
        }
    }
    
    func addFiles() throws {
        let filePath = consoleInput(annotation: "Enter file path: ")
        do {
            try JSOC.fileManager.copyItem(atPath: filePath, toPath: JSOC.fileManager.currentDirectoryPath)
            JSOC.fileManager.homeDirectory(forUser: "")
        } catch {
            print("[!] No such file exists!!")
            print(error.localizedDescription)
            exit(EXIT_FAILURE)
        }
        
    }
    
    func modifyProject() {
        
    }
    
    func deleteProject() {
        
    }
    
    func exportProject() {
        do {
            var projects = Project.readProjects()
            if !projects.contains(self){
                    projects.append(self)
            }
            try JSOC.saveJSON(data: projects)
        } catch {
            print(error.localizedDescription)
            exit(EXIT_FAILURE)
        }
    }
    
    
}


// MARK:- Task Handler

enum Priority: String, Codable {
    case low
    case medium
    case high
}

enum Status: String, Codable {
    case abort
    case waiting
    case inProgress
    case completed
}

protocol CoreTask: Codable {
    var key: String { get set }
    var priority: Priority { get set }
    var objective: String { get set }
    var description: String { get set }
    var start: String? { get set }
    var end: String? { get set }
    var status: Status { get set }
    var dependentOn: String? { get set }
    var projectId: String  { get set }
    var author: String { get set }
    
    static func newTask(account: Account, project: inout Project) -> Self
    func addReminder()
    
}


struct Task: CoreTask {
    
    var key: String
    
    var priority: Priority
    
    var objective: String
    
    var description: String
    
    var start: String?
    
    var end: String?
    
    var status: Status
        
    var dependentOn: String?
    
    var projectId: String
    
    var author: String
    
    
    static func newTask(account: Account, project: inout Project) -> Task {
        var key = consoleInput(annotation: "Enter task id (Optional) :", required: false)
        if key.isEmpty {
            key = UUID().uuidString
        }
        let priority = consoleInput(annotation: "Enter priority [low|medium|high]: ")
        let objective = consoleInput(annotation: "Enter task objective: ")
        let desc = consoleInput(annotation: "Enter task description: ")
        let start = consoleInput(annotation: "Enter start date (Optional)", required: false).engageSecure()
        let end = consoleInput(annotation: "Enter expected end date (Optional): ", required: false).engageSecure()
        let status = consoleInput(annotation: "Enter current status [ waiting | inProgress | completed | abort ]")
        let dependency = consoleInput(annotation: "Enter comma separated task id(s) this task depends on (Optional): ", required: false).engageSecure()
        
        
        let task = Task(key: key, priority: Priority(rawValue: priority)!, objective: objective, description: desc, start: start, end: end, status: Status(rawValue: status)!, dependentOn: dependency, projectId: project.id, author: account.username)
        
        project.tasks.append(task)
        
        return task
        
    }
    
    func addReminder() {
        
    }
}


var account = Account.newAccount()

var project = Project.createNewProject(account: &account)

let task = Task.newTask(account: account, project: &project)

do {
    try project.addFiles()
} catch {
    print("[!] Copying failed")
    print(error.localizedDescription)
}
account.exportAccount(encrypted: false)
