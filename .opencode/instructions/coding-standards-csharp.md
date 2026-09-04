# C# Coding Standards

## General Principles

1. **Readability First**: Write code that is easy to read and understand
2. **Consistency**: Follow established patterns throughout the codebase
3. **Simplicity**: Prefer simple solutions over complex ones
4. **Maintainability**: Write code that is easy to modify and extend

## Naming Conventions

### PascalCase
- **Classes**: `UserService`, `OrderProcessor`
- **Interfaces**: `IUserService`, `IOrderProcessor`
- **Public Methods**: `GetUserById`, `ProcessOrder`
- **Properties**: `UserId`, `OrderTotal`
- **Constants**: `MaxRetryCount`, `DefaultTimeout`
- **Enums**: `OrderStatus`, `UserRole`
- **Events**: `OrderPlaced`, `UserLoggedIn`

### camelCase
- **Private Fields**: `_userService`, `_orderProcessor`
- **Local Variables**: `userId`, `orderTotal`
- **Parameters**: `userId`, `orderTotal`
- **Method Parameters**: `string userId`, `int orderTotal`

### snake_case (for specific cases)
- **Private Constants**: `_max_retry_count`
- **Private Static Readonly**: `_default_timeout`

## File Organization

1. **One class per file** (except small nested classes)
2. **File name matches class name**
3. **Organize by feature** when possible:
   ```
   Features/
   ├── Users/
   │   ├── UserService.cs
   │   ├── UserController.cs
   │   └── UserDto.cs
   └── Orders/
       ├── OrderService.cs
       ├── OrderController.cs
       └── OrderDto.cs
   ```

## Class Structure

```csharp
// 1. Using directives
using System;
using System.Collections.Generic;

// 2. Namespace
namespace MyApp.Features.Users
{
    // 3. Class declaration
    public class UserService
    {
        // 4. Private fields
        private readonly IUserRepository _userRepository;
        
        // 5. Constructor
        public UserService(IUserRepository userRepository)
        {
            _userRepository = userRepository;
        }
        
        // 6. Public properties
        public bool IsInitialized { get; private set; }
        
        // 7. Public methods
        public async Task<User> GetUserByIdAsync(int userId)
        {
            return await _userRepository.GetByIdAsync(userId);
        }
        
        // 8. Private methods
        private void Initialize()
        {
            IsInitialized = true;
        }
    }
}
```

## Method Guidelines

### Small and Focused
- Methods should do one thing well
- Maximum 20-30 lines (guideline, not strict rule)
- Extract complex logic into helper methods

### Parameters
- Maximum 3-4 parameters
- Use objects for complex parameter lists
- Prefer `CancellationToken` as last parameter for async methods

```csharp
// Good
public async Task<User> GetUserAsync(
    int userId,
    CancellationToken cancellationToken = default)
{
    return await _userRepository.GetByIdAsync(userId, cancellationToken);
}

// Better for complex cases
public async Task<User> GetUserAsync(
    GetUserRequest request,
    CancellationToken cancellationToken = default)
{
    return await _userRepository.GetByIdAsync(request.UserId, cancellationToken);
}
```

### Return Types
- Use `Task<T>` for async methods
- Use `ValueTask<T>` for hot paths with potential synchronous completion
- Use `IEnumerable<T>` or `IAsyncEnumerable<T>` for collections

## Async/Await Patterns

```csharp
// Always use CancellationToken
public async Task<User> GetUserAsync(int userId, CancellationToken cancellationToken)
{
    return await _userRepository.GetByIdAsync(userId, cancellationToken);
}

// Configure await for performance-critical code
public async Task ProcessOrderAsync(Order order, CancellationToken cancellationToken)
{
    await _orderRepository.SaveAsync(order, cancellationToken).ConfigureAwait(false);
}

// Use ConfigureAwait(false) in library code
public async Task<Results> GetResultsAsync(CancellationToken cancellationToken)
{
    return await _dataProvider.GetResultsAsync(cancellationToken).ConfigureAwait(false);
}
```

## Error Handling

```csharp
// Use specific exceptions
public class UserNotFoundException : Exception
{
    public int UserId { get; }
    
    public UserNotFoundException(int userId)
        : base($"User with ID {userId} not found")
    {
        UserId = userId;
    }
}

// Use try-catch for recoverable errors
public async Task<User> GetUserAsync(int userId, CancellationToken cancellationToken)
{
    try
    {
        return await _userRepository.GetByIdAsync(userId, cancellationToken);
    }
    catch (UserNotFoundException)
    {
        _logger.LogWarning("User {UserId} not found", userId);
        throw;
    }
}
```

## Dependency Injection

```csharp
// Register services with appropriate lifetime
services.AddScoped<IUserService, UserService>();
services.AddSingleton<ICacheService, CacheService>();
services.AddTransient<IEmailSender, EmailSender>();

// Use constructor injection
public class OrderService
{
    private readonly IUserService _userService;
    private readonly IOrderRepository _orderRepository;
    
    public OrderService(
        IUserService userService,
        IOrderRepository orderRepository)
    {
        _userService = userService;
        _orderRepository = orderRepository;
    }
}
```

## Testing

```csharp
// Use descriptive test names
[Fact]
public async Task GetUserById_WhenUserExists_ReturnsUser()
{
    // Arrange
    var userId = 1;
    var expectedUser = new User { Id = userId, Name = "Test User" };
    _userRepository.GetByIdAsync(userId).Returns(expectedUser);
    
    // Act
    var result = await _userService.GetUserByIdAsync(userId);
    
    // Assert
    Assert.Equal(expectedUser, result);
}

// Use meaningful assertions
[Fact]
public async Task GetUserById_WhenUserDoesNotExist_ThrowsUserNotFoundException()
{
    // Arrange
    var userId = 999;
    _userRepository.GetByIdAsync(userId).Throws(new UserNotFoundException(userId));
    
    // Act & Assert
    await Assert.ThrowsAsync<UserNotFoundException>(
        () => _userService.GetUserByIdAsync(userId));
}
```

## Code Analysis

- Use **Microsoft.CodeAnalysis.NetAnalyzers** for static analysis
- Follow **CA** rules for code quality
- Follow **IDE** rules for IDE suggestions
- Use **Nullable reference types** enabled project-wide

## Documentation

- Use XML documentation for public APIs
- Use `/// <summary>` for method descriptions
- Use `/// <param>` for parameter descriptions
- Use `/// <returns>` for return value descriptions
- Use `/// <exception>` for exceptions that may be thrown

```csharp
/// <summary>
/// Gets a user by their unique identifier.
/// </summary>
/// <param name="userId">The unique identifier of the user.</param>
/// <param name="cancellationToken">Cancellation token.</param>
/// <returns>The user if found; otherwise, null.</returns>
/// <exception cref="ArgumentNullException">Thrown when userId is null.</exception>
public async Task<User?> GetUserByIdAsync(
    int userId,
    CancellationToken cancellationToken = default)
{
    return await _userRepository.GetByIdAsync(userId, cancellationToken);
}
```
