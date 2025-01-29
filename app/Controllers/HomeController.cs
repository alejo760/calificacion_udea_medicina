using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Rendering;
using System.Net.Http.Json;

public class HomeController : Controller
{
    private readonly IHttpClientFactory _clientFactory;
    private readonly ILogger<HomeController> _logger;
    private const string BaseApiUrl = "http://localhost:8000/moodle/";

    public HomeController(IHttpClientFactory clientFactory, ILogger<HomeController> logger)
    {
        _clientFactory = clientFactory;
        _logger = logger;
    }

    public async Task<IActionResult> Index()
    {
        var model = new MoodleFrontendModel();
        
        try
        {
            var client = _clientFactory.CreateClient();
            var response = await client.GetAsync($"{BaseApiUrl}courses");
            
            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadFromJsonAsync<Dictionary<string, List<Course>>>();
                if (content != null && content.ContainsKey("courses"))
                {
                    model.Courses = content["courses"] ?? new List<Course>();
                }
            }
            else
            {
                _logger.LogError($"Error getting courses: {response.StatusCode}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error fetching courses from API");
        }

        return View(model);
    }

    [HttpPost]
    public async Task<IActionResult> Enroll(IFormFile studentsFile, string courseId, string roleId, bool generateQr)
    {
        if (studentsFile == null || string.IsNullOrEmpty(courseId) || string.IsNullOrEmpty(roleId))
        {
            return RedirectToAction("Index");
        }

        var client = _clientFactory.CreateClient();
        
        using var content = new MultipartFormDataContent();
        content.Add(new StreamContent(studentsFile.OpenReadStream()), "studentsFile", studentsFile.FileName);
        content.Add(new StringContent(courseId), "courseId");
        content.Add(new StringContent(roleId), "roleId");
        content.Add(new StringContent(generateQr.ToString().ToLower()), "generateQr");

        var response = await client.PostAsync($"{BaseApiUrl}enroll", content);

        if (response.Content.Headers.ContentType.MediaType == "application/x-zip-compressed")
        {
            var stream = await response.Content.ReadAsStreamAsync();
            return File(stream, "application/zip", "qr_codes.zip");
        }

        var result = await response.Content.ReadFromJsonAsync<Dictionary<string, object>>();
        return View("Results", result);
    }

    [HttpPost]
    public async Task<IActionResult> Grade(int studentId, int courseId, decimal grade)
    {
        if (studentId <= 0 || courseId <= 0 || grade < 0)
        {
            TempData["Error"] = "Invalid input data";
            return RedirectToAction("Index");
        }

        var client = _clientFactory.CreateClient();
        var response = await client.PostAsJsonAsync($"{BaseApiUrl}grade", new
        {
            student_id = studentId,
            course_id = courseId,
            grade = grade
        });

        if (response.IsSuccessStatusCode)
        {
            TempData["Message"] = "Grade updated successfully!";
        }
        else
        {
            TempData["Error"] = "Error updating grade";
        }

        return RedirectToAction("Index");
    }

    public IActionResult Results()
    {
        return View();
    }
}