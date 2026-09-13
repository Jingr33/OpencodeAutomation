# C# Coding Standards

These standards apply when working on C#/.NET target repositories. They do not
change the language-agnostic conventions of this Python automation framework;
follow the target repository's instructions when they are more specific.

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
- **Local Variables**: `userId`, `orderTotal`
- **Parameters**: `userId`, `orderTotal`
- **Method Parameters**: `string userId`, `int orderTotal`

### Private Fields (underscore-prefixed camelCase)
- **Private Fields**: `_userService`, `_orderProcessor`

### Protected Members
- **Protected Fields**: Use the underscore-prefixed camelCase convention, such as `_userService`.
- **Protected Properties, Methods, and Events**: Use PascalCase, such as `UserId` or `Initialize`.
- Use protected members deliberately because they form part of the contract for derived classes.

### PascalCase (for specific cases)
- **Private Constants**: `MaxRetryCount`, `DefaultTimeout`
- **Private Static Readonly**: `DefaultTimeout`

## File Organization

1. **One type per file** (nested types are the exception; do not place multiple top-level classes, records, or enums in one file)
2. **File name matches the primary type name**
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
using System.Threading.Tasks;

// 2. Namespace
namespace MyApp.Features.Users
{
    // 3. Class declaration and primary constructor (C# 12+)
    public class UserService(IUserRepository userRepository)
    {
        // 4. Public properties
        public bool IsInitialized { get; private set; }
        
        // 5. Public instance methods
        public async Task<User> GetUserByIdAsync(int userId)
        {
            return await userRepository.GetByIdAsync(userId);
        }
        
        // 6. Private methods
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
- For many related parameters, use a `record`, `record struct`, or `struct` to transfer them as one value
- Prefer `CancellationToken` as last parameter for async methods

```csharp
public readonly record struct GetUserRequest(int UserId);
```

Keep a production request type in its own file. Use a `record struct` for small value-like requests and a `record` when reference semantics are more appropriate.

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

- Use a semicolon for declarations without an implementation, such as interface
  or abstract members; use braces only when declaring a type or providing an
  implementation.

### Method Ordering and Static Methods
- Place public instance methods before public static methods when organizing a type.
- Keep related static methods together under the instance methods rather than mixing them into the instance API.
- When a type accumulates many cohesive static methods, consider extracting them into a dedicated static extension-method class when those methods naturally extend another type.

### Return Types
- Use `Task<T>` for async methods
- Use `ValueTask<T>` for hot paths with potential synchronous completion
- Use `IEnumerable<T>` or `IAsyncEnumerable<T>` for collections

## Async/Await Patterns

The examples in this section apply to C#/.NET target repositories. Use
`ConfigureAwait(false)` deliberately in reusable library code when avoiding
context capture is part of the target project's design. Do not add it
universally to application code; follow the target repository's established
conventions.

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

// Use ConfigureAwait(false) deliberately in reusable library code
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

## Inheritance and Abstract Classes

- Use abstract classes and inheritance when they provide meaningful reuse or a shared base for derived types.
- Name an abstract base class with the `Base` suffix, such as `RepositoryBase`.
- Interfaces should use the normal `I` prefix and should not receive the `Base` suffix.

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
