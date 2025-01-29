using Microsoft.AspNetCore.Mvc.Rendering;
public class MoodleFrontendModel
{
    public List<Course> Courses { get; set; } = new List<Course>();
    public List<SelectListItem> CourseList => Courses
        .Select(c => new SelectListItem { Value = c.CourseId.ToString(), Text = $"{c.CourseId} - {c.CourseName}" })
        .ToList();
}

public class Course
{
    public int CourseId { get; set; }
    public required string CourseName { get; set; }
}