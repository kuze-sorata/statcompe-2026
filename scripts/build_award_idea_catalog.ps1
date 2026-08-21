param(
    [string]$IndexPath = "references/awards/index.csv",
    [string]$OutputPath = "references/awards/idea-catalog.md"
)

$ErrorActionPreference = "Stop"

function Normalize-Text([string]$Value) {
    if ([string]::IsNullOrWhiteSpace($Value)) { return "" }
    return (($Value -replace "\s+", " ").Trim())
}

function Clip-Text([string]$Value, [int]$Limit = 150) {
    $clean = Normalize-Text $Value
    if ($clean.Length -le $Limit) { return $clean }
    return $clean.Substring(0, $Limit).Trim() + "…"
}

function Find-Target([string]$Text, [string]$Title) {
    $patterns = @(
        '(.{2,100}?(?:率|数|額|量|時間|所得|価格|能力|得点|割合|指数))を(?:目的変数|被説明変数|従属変数)(?:とする|として)',
        '(?:目的変数|被説明変数|従属変数)(?:には|は|として|を)?[、：:]?\s*[「『]?([^。\n」』]{2,90})',
        '(?:分析対象|中心指標)(?:には|は|として)?[、：:]?\s*(.{2,160}?)(?:。|\n)'
    )
    foreach ($pattern in $patterns) {
        $match = [regex]::Match($Text, $pattern)
        if ($match.Success) {
            $candidate = if ($match.Groups.Count -gt 1) { $match.Groups[1].Value } else { $match.Value }
            $candidate = Clip-Text $candidate 135
            $candidate = $candidate -replace '^.*(?:用いたのが|使用したのが)[「『]?', ''
            if (
                $candidate.Length -ge 2 -and
                $candidate -notmatch '説明変数|係数|誤差項|𝑥|β|式を以下|除外|とするもの' -and
                $candidate -match '(率|数|額|量|時間|所得|価格|能力|得点|割合|指数|成績|台数|需要|支出|人口)$'
            ) { return $candidate }
        }
    }
    $targets = [ordered]@{
        '女性議員'='女性議員比率'; '精神疾患休職'='精神疾患による教員休職率'; '持久力'='シャトルラン成績などの持久力指標'; 'MRI'='MRI設置台数';
        'CO\s*2|CO2|二酸化炭素'='CO2排出量・排出構成'; '女性の社会進出|女性社会進出'='女性就業率・女性の労働参加指標'; 'デジタル教科書'='学力調査の得点';
        '所得格差'='所得水準・所得格差指標'; '地方移住|人口移動|人口流出|人口流動|社会増減|人口変動|人口増減'='転入・転出または社会増減率';
        '消滅可能性|過疎化'='人口減少率・消滅可能性に関する人口指標'; '合計特殊出生率|出生率|少子化'='合計特殊出生率・出生数';
        '自殺'='自殺者数・自殺死亡率'; '自己肯定感'='自己肯定感に関する回答指標'; '不登校'='不登校児童生徒数・不登校率';
        '医師'='人口当たり医師数・医師偏在指標'; '医療費'='一人当たり医療費'; '介護職の離職'='介護職員の離職率'; '介護.*従業者'='介護業界の従業者数';
        '宿泊'='宿泊者数・宿泊需要'; '観光消費'='観光消費額'; '観光'='観光客数・観光関連指標'; '英語'='英語力・英語学力指標';
        '学力|基礎学力|学習状況'='全国学力・学習状況調査等の学力指標'; '体力|運動能力'='体力・運動能力調査の得点';
        '投票率'='選挙投票率'; '犯罪'='犯罪認知件数・犯罪率'; '交通事故'='交通事故発生件数・発生率'; '火災'='建物火災発生率';
        'ごみ|リサイクル'='ごみ排出量・リサイクル率'; '空き家'='空き家数・空き家率'; '地価|住宅価格'='地価・住宅価格';
        '健康寿命'='健康寿命'; '脳卒中'='脳卒中の発症・死亡指標'; '大腸がん'='大腸がん罹患率'; 'う蝕'='う蝕罹患率';
        '金融資産'='株式・投資信託・外貨預金の購入経験者割合'; 'ふるさと納税'='ふるさと納税額と所得・人口増減指標';
        '失業率'='完全失業率'; '最低賃金'='地域別最低賃金'; '幸福度'='主観的幸福度'; '睡眠時間'='平均睡眠時間';
        '電力需要'='電力需要量'; '食料自給率'='食料自給率'; '降水量'='降水量'; '鳥獣被害'='鳥獣被害額・被害面積';
        '離婚'='離婚率・離婚件数'; '外国人'='外国人人口・外国人居住／就労指標'; 'ボランティア'='ボランティア活動率・参加率';
        '教育費'='学力と教育費の費用対効果'; '大学.*進学率|進学率'='大学等進学率'; '人口集中'='一人当たり県民所得';
        '金融教育'='金融資産購入経験者割合'; '保育所|待機児童'='保育所利用・定員充足率または待機児童数';
        'ワークライフバランス'='労働時間・生活時間などのワークライフバランス指標'; '住宅'='住宅需要・住宅特性';
        '食の外部化'='外食・中食への支出割合'; '食料費支出'='家計の食料費支出'; '消費重心|家計消費'='品目別消費支出・消費重心';
        'ヤングケアラー'='ヤングケアラーに対する認知・意識'; 'デジタル.*格差|IT社会'='情報通信利用・デジタル格差指標';
        'テレワーク'='テレワーク実施率・通勤時間'; '学習意欲'='学習意欲に関する回答指標'; 'マダコ|いかなご'='漁獲量';
        'ドクターヘリ'='ドクターヘリの配置・出動圏域'; '景気'='景気動向・経済活動指標'; '新型コロナ|感染者'='新型コロナ感染者数・感染率';
        '人手不足'='労働需給・潜在的な人手不足指標'; '技能実習生'='外国人技能実習生の就労地・人数'; '女性就業'='女性就業率';
        '人口の自然増減'='自然増減率'; '人口'='人口増減率・人口構成';
        '地方創生'='人口増減率・自然増減率・社会増減率などの地域活力指標';
    }
    foreach ($entry in $targets.GetEnumerator()) {
        if ($Title -match $entry.Key) { return $entry.Value }
    }
    return "論文が中心的に比較・分類する「$Title」に対応する指標"
}

function Find-SsdseRole([string]$Text) {
    if ($Text -notmatch 'SSDSE') { return "本文にSSDSE利用の明記を確認できず、外部統計または独自データが中心" }
    $context = ([regex]::Matches($Text, '.{0,100}SSDSE.{0,170}', 'IgnoreCase') | ForEach-Object { Normalize-Text $_.Value }) -join ' '
    if ($context -match '目的変数|被説明変数|従属変数') { return "目的変数または中心指標の取得に使用" }
    if ($context -match '総人口|人口総数|65歳|15歳|年齢|分母|人口構成') { return "人口規模・年齢構成の算出、比率の分母または統制変数として使用" }
    if ($context -match '気温|降水|積雪|日照|気象') { return "気候・自然環境を表す説明変数として使用" }
    if ($context -match '就業|産業|所得|財政|人口密度|面積|事業所|教育|医師|病院|学校') { return "地域の社会経済構造・供給条件を表す説明変数または統制変数として使用" }
    if ($context -match '主として|主に|全て|データセットを構築') { return "分析データの基盤として複数の目的・説明指標に使用" }
    return "地域比較の基礎指標・説明変数として使用"
}

function Find-Sources([string]$Text) {
    $sourcePatterns = [ordered]@{
        'e-Stat' = 'e-?Stat'
        '総務省' = '総務省'
        '文部科学省' = '文部科学省'
        '厚生労働省' = '厚生労働省'
        '国土交通省・観光庁' = '国土交通省|観光庁'
        '環境省' = '環境省'
        '農林水産省' = '農林水産省'
        '内閣府' = '内閣府'
        '警察庁' = '警察庁'
        '消防庁' = '消防庁'
        '気象庁' = '気象庁'
        'スポーツ庁' = 'スポーツ庁'
        '国勢調査' = '国勢調査'
        '人口動態統計' = '人口動態統計'
        '家計調査' = '家計調査'
        '学校基本調査' = '学校基本調査'
        '全国学力・学習状況調査' = '全国学力.{0,4}学習状況調査'
        '病床機能報告' = '病床機能報告'
    }
    $found = [System.Collections.Generic.List[string]]::new()
    foreach ($entry in $sourcePatterns.GetEnumerator()) {
        if ($Text -match $entry.Value) { $found.Add($entry.Key) }
        if ($found.Count -ge 5) { break }
    }
    if ($found.Count -eq 0) { return "論文本文に記載された公表統計・調査データ（原本PDF参照）" }
    return ($found -join '、')
}

function Make-Question([string]$Title) {
    $base = (($Title -replace '―.*$', '') -replace '\s+-[^-].*$', '')
    $base = Normalize-Text $base
    if ($base -match '[?？]$') { return $base }
    if ($base -match '要因|決定要因|原因|影響|関係|メカニズム|左右') {
        return "${base}――観察された地域差や時系列変化を生む条件は何か"
    }
    return "${base}を地域差として捉えたとき、差を生む条件と改善可能な要因は何か"
}

$root = (Resolve-Path ".").Path
$rows = Import-Csv -Encoding UTF8 $IndexPath | Where-Object { $_.kind -eq 'paper' }
$lines = [System.Collections.Generic.List[string]]::new()
$lines.Add('# 過去受賞論文・アイデア発想索引')
$lines.Add('')
$lines.Add('統計データ分析コンペティションの2018〜2025年受賞論文159本を、テーマ探索のために同じ形式で整理した。回帰分析の論文は目的変数、指標作成・分類・記述型の論文は中心指標を「目的変数」欄に記載する。説明材料は本文中で確認できた主な公表主体・統計であり、厳密な変数定義はリンク先の原本PDFで確認する。')
$lines.Add('')
$lines.Add('この索引は、SSDSEの項目からテーマを逆算するためのものではない。受賞論文がどの外部現象を中心に据え、SSDSEを目的変数、説明変数、分母、統制変数のどこへ配置したかを比較するための発想用索引である。')

foreach ($year in ($rows.year | Sort-Object -Descending -Unique)) {
    $lines.Add('')
    $lines.Add("## $year 年")
    foreach ($division in @('大学生・一般の部', '高校生の部')) {
        $subset = $rows | Where-Object { $_.year -eq $year -and $_.division -eq $division }
        if (-not $subset) { continue }
        $lines.Add('')
        $lines.Add("### $division")
        foreach ($row in $subset) {
            $text = Get-Content -Raw -Encoding UTF8 $row.text_path
            $pdfPath = (($root + '/' + $row.local_path) -replace '\\', '/')
            $target = Find-Target $text $row.title
            $sources = Find-Sources $text
            $ssdse = Find-SsdseRole $text
            $question = Make-Question $row.title
            $lines.Add('')
            $lines.Add("#### $($row.year)年・$($row.award)")
            $lines.Add('')
            $lines.Add("[$($row.title)]($pdfPath)")
            $lines.Add('')
            $lines.Add("中心テーマ：$($row.title)")
            $lines.Add("目的変数・中心指標：$target")
            $lines.Add("主な説明材料：$sources")
            $lines.Add("SSDSEの役割：$ssdse")
            $lines.Add("問い：$question")
        }
    }
}

$outputDirectory = Split-Path -Parent $OutputPath
if ($outputDirectory -and -not (Test-Path $outputDirectory)) {
    New-Item -ItemType Directory -Path $outputDirectory | Out-Null
}
$lines | Set-Content -Encoding UTF8 $OutputPath

Write-Output "Wrote $($rows.Count) papers to $OutputPath"
