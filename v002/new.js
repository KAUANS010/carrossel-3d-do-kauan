// Função para criar a lista de links
function criarListaLinks(qualLista, qualVetor) {
  const listaEl = document.getElementById(qualLista);

  qualVetor.forEach(link => {
    // Criar elemento li
    const li = document.createElement('li');
    li.className = 'item';

    // Criar elemento de link
    const a = document.createElement('a');
    a.href = link.href;
    a.target = "_blank"; // Abre em nova aba

    // Criar imagem
    const img = document.createElement('img');
    img.src = link.img;
    img.alt = link.alt;

    // Criar parágrafo para o texto
    const p = document.createElement('p');
    p.textContent = link.alt;

    // Montar a estrutura
    a.appendChild(img);
    a.appendChild(p);
    li.appendChild(a);
    listaEl.appendChild(li);
  });
}

// Função para carregar dados de um arquivo JSON
async function carregarDados(arquivo) {
  try {
    const resposta = await fetch(arquivo);
    if (!resposta.ok) {
      throw new Error(`Erro ao carregar ${arquivo}: ${resposta.status}`);
    }
    return await resposta.json();
  } catch (erro) {
    console.error(`Falha ao carregar ${arquivo}:`, erro);
    return []; // Retorna array vazio em caso de erro
  }
}

// Executar quando o documento estiver carregado
document.addEventListener('DOMContentLoaded', async function () {
  try {
    // Carregar os dados dos arquivos JSON
    const links = await carregarDados('./links.json');
    const linksKns1 = await carregarDados('./linksKns1.json');
    const linksKns2 = await carregarDados('./linksKns2.json');
    const linksKns3 = await carregarDados('./linksKns3.json');
    
    // Criar as listas com os dados carregados
    criarListaLinks('lista-horizontal', links);
    criarListaLinks('lista-kns', linksKns1);
    criarListaLinks('lista-kns-linha2', linksKns2);
    criarListaLinks('lista-kns-linha3', linksKns3);
    
    console.log('Dados carregados com sucesso!');
  } catch (erro) {
    console.error('Erro ao inicializar a aplicação:', erro);
  }
});