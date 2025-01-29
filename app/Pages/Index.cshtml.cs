using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;

namespace app.Pages;

public class IndexModel : PageModel
{
    private readonly ILogger<IndexModel> _logger;
    public string Message { get; set; }

    public IndexModel(ILogger<IndexModel> logger)
    {
        _logger = logger;
    }

    public void OnGet()
    {
        Message = "Bienvenido al sistema de calificación UdeA Medicina";
        _logger.LogInformation("Página Index cargada en: {Time}", DateTime.UtcNow);
    }
}
