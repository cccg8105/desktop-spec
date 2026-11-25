using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace SampleNotes.Modules.Notes
{
    public sealed class CreateNoteUseCase : INotesModule
    {
        private readonly List<Note> _notes = new();

        public Task<Note> CreateAsync(string title, string body, CancellationToken cancellationToken = default)
        {
            cancellationToken.ThrowIfCancellationRequested();
            var note = Note.Create(title, body);
            _notes.Add(note);
            return Task.FromResult(note);
        }

        public Task<IReadOnlyList<Note>> ListAsync(CancellationToken cancellationToken = default)
        {
            cancellationToken.ThrowIfCancellationRequested();
            IReadOnlyList<Note> snapshot = _notes.AsReadOnly();
            return Task.FromResult(snapshot);
        }
    }
}
