<h1>TermosSync SFTP</h1>

<p>
  Sincronizador <strong>SFTP → Pasta de Rede</strong> para manter
  <em>\\fs01\ITAPEVA ATIVAS\JURIDICO\--- TERMOS DE CESSÃO ---</em>
  idêntica ao diretório remoto (por <strong>nome + tamanho</strong>).
</p>

<hr />

<h2>O que ele faz</h2>
<ul>
  <li>Varre o diretório remoto (recursivo) e a pasta local (recursivo)</li>
  <li>Compara arquivos por <strong>caminho relativo + tamanho</strong></li>
  <li>Se for igual: não altera</li>
  <li>Se estiver diferente ou faltando local: baixa e substitui</li>
  <li>Se existir só no local: remove (espelhamento do remoto)</li>
  <li>Gera <strong>log em TXT</strong> por execução</li>
</ul>

<h2>Estrutura</h2>
<ul>
  <li><code>sync_termos.py</code> — script principal</li>
  <li><code>\\fs01\ITAPEVA ATIVAS\JURIDICO\--- TERMOS DE CESSÃO ---\Logs</code> — logs gerados</li>
  <li><code>\\fs01\ITAPEVA ATIVAS\DADOS\SA_Credencials.txt</code> — credenciais (sintaxe Python)</li>
</ul>

<h2>Pré-requisitos</h2>
<ul>
  <li>Python 3.10+ (recomendado)</li>
  <li>Biblioteca <code>paramiko</code></li>
  <li>Acesso à pasta de rede e ao SFTP</li>
</ul>

<h2>Instalação</h2>
<pre><code>pip install paramiko</code></pre>

<h2>Configuração</h2>
<p>
  O script lê as credenciais do arquivo:
  <br />
  <code>\\fs01\ITAPEVA ATIVAS\DADOS\SA_Credencials.txt</code>
</p>

<p>Variáveis esperadas no TXT:</p>
<ul>
  <li><code>SFTP_HOST_ORIG</code></li>
  <li><code>SFTP_PORT_ORIG</code></li>
  <li><code>SFTP_USERNAME_ORIG</code></li>
  <li><code>SFTP_PASSWORD_ORIG</code></li>
  <li><code>REMOTE_DIR_ORIG</code> (ex: <code>/FTP/</code>)</li>
</ul>

<h2>Como usar</h2>
<p>Execute o script:</p>
<pre><code>python sync_termos.py</code></pre>

<p>
  Na primeira execução (pasta vazia), ele baixa tudo do remoto.
  Nas próximas, mantém a pasta local espelhada.
</p>

<h2>Logs</h2>
<p>
  Cada execução gera um arquivo TXT em:
  <br />
  <code>\\fs01\ITAPEVA ATIVAS\JURIDICO\--- TERMOS DE CESSÃO ---\Logs</code>
</p>
<p>Formato do arquivo:</p>
<pre><code>sync_termos_YYYYMMDD_HHMMSS.txt</code></pre>

<h2>Notas</h2>
<ul>
  <li>O critério de igualdade é <strong>nome + tamanho</strong>.</li>
  <li>Arquivos que existem apenas localmente são removidos para manter espelho do remoto.</li>
  <li>Se quiser comparar também por data/hora (mtime) ou hash, dá para evoluir facilmente.</li>
</ul>

<hr />

