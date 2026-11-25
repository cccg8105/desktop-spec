using System;

namespace SampleNotes.Modules.Notes
{
    public sealed record Note(
        Guid Id,
        string Title,
        string Body,
        DateTimeOffset CreatedAtUtc)
    {
        public static Note Create(string title, string body)
        {
            if (string.IsNullOrWhiteSpace(title))
            {
                throw new ArgumentException("El titulo de la nota es obligatorio.", nameof(title));
            }

            if (title.Trim().Length > 120)
            {
                throw new ArgumentException("El titulo no puede exceder 120 caracteres.", nameof(title));
            }

            return new Note(
                Guid.NewGuid(),
                title.Trim(),
                body?.Trim() ?? string.Empty,
                DateTimeOffset.UtcNow);
        }
    }
}
