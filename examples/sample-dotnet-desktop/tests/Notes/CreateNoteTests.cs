using System;
using System.Threading.Tasks;
using SampleNotes.Modules.Notes;

namespace SampleNotes.Tests.Notes
{
    public sealed class CreateNoteTests
    {
        public async Task CreateAsync_ValidInput_PersistsNote()
        {
            var useCase = new CreateNoteUseCase();
            var note = await useCase.CreateAsync("Nota de prueba", "Contenido inicial");

            if (note.Id == Guid.Empty)
            {
                throw new InvalidOperationException("Se esperaba un identificador valido.");
            }

            var list = await useCase.ListAsync();
            if (list.Count != 1)
            {
                throw new InvalidOperationException("Se esperaba una nota almacenada.");
            }
        }

        public async Task CreateAsync_EmptyTitle_ThrowsArgumentException()
        {
            var useCase = new CreateNoteUseCase();
            try
            {
                await useCase.CreateAsync("   ", "Contenido");
                throw new InvalidOperationException("Se esperaba ArgumentException para titulo vacio.");
            }
            catch (ArgumentException)
            {
                // Comportamiento esperado por regla BR-01
            }
        }
    }
}
