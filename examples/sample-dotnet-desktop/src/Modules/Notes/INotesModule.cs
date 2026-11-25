using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace SampleNotes.Modules.Notes
{
    public interface INotesModule
    {
        Task<Note> CreateAsync(string title, string body, CancellationToken cancellationToken = default);
        Task<IReadOnlyList<Note>> ListAsync(CancellationToken cancellationToken = default);
    }
}
