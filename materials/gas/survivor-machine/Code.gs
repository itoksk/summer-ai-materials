/**
 * Survivor Machine — class data collection (GAS Web App)
 * 各生徒の Titanic プロフィールと「自分は助かると思うか?」の予想を集め、
 * モデル判定(サイトの決定木と同じ)と照合してクラス集計を返す。
 *
 * 設計ルール(gas-spreadsheet)準拠:
 *  - SPREADSHEET_ID は PropertiesService 管理(ハードコード禁止)、初回自動作成
 *  - timestamp は Utilities.formatDate() で文字列化してから書き込む
 *  - カラムアクセスは headerMap パターン(インデックス直指定禁止)
 *  - ID は Utilities.getUuid()、削除はソフトデリート(status=ARCHIVED)
 *  - 全関数 try-catch + 構造化レスポンス { success, data, error }
 */

var SHEET_NAME = 'responses';
var HEADERS = ['id', 'timestamp', 'nickname', 'sex', 'pclass', 'age', 'guess', 'modelProb', 'modelVerdict', 'status'];

function doGet() {
  return HtmlService.createHtmlOutputFromFile('index')
    .setTitle('Survivor Machine — クラス集計')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1');
}

// ----- spreadsheet bootstrap (auto-create on first access) -----
function getSpreadsheet_() {
  var props = PropertiesService.getScriptProperties();
  var id = props.getProperty('SPREADSHEET_ID');
  if (id) {
    try {
      return SpreadsheetApp.openById(id);
    } catch (e) {
      // fall through and recreate
    }
  }
  var ss = SpreadsheetApp.create('Survivor Machine Responses');
  props.setProperty('SPREADSHEET_ID', ss.getId());
  var sheet = ss.getSheets()[0];
  sheet.setName(SHEET_NAME);
  sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
  return ss;
}

function getSheet_() {
  var ss = getSpreadsheet_();
  var sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
  }
  return sheet;
}

function headerMap_(sheet) {
  var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  var map = {};
  headers.forEach(function (h, i) { map[h] = i; });
  return map;
}

// ----- model: mirrors the website's decision tree exactly -----
function modelPredict_(sex, pclass, age) {
  pclass = Number(pclass);
  age = Number(age);
  var prob;
  if (sex === 'female') {
    prob = pclass === 1 ? 0.97 : (pclass === 2 ? 0.92 : 0.5);
  } else if (age <= 6) {
    prob = pclass === 3 ? 0.36 : 0.83;
  } else {
    prob = pclass === 1 ? 0.36 : 0.13;
  }
  return { prob: prob, verdict: prob >= 0.5 ? 'survive' : 'dies' };
}

// ----- write one response -----
function submitResponse(payload) {
  try {
    if (!payload || (payload.sex !== 'female' && payload.sex !== 'male')) {
      return { success: false, error: 'invalid payload' };
    }
    var sheet = getSheet_();
    var model = modelPredict_(payload.sex, payload.pclass, payload.age);
    var tz = Session.getScriptTimeZone() || 'Asia/Tokyo';
    var ts = Utilities.formatDate(new Date(), tz, 'yyyy-MM-dd HH:mm:ss');
    var record = {
      id: Utilities.getUuid(),
      timestamp: ts,
      nickname: String(payload.nickname || '').slice(0, 40),
      sex: payload.sex,
      pclass: Number(payload.pclass),
      age: Number(payload.age),
      guess: payload.guess === 'survive' ? 'survive' : 'dies',
      modelProb: model.prob,
      modelVerdict: model.verdict,
      status: 'ACTIVE'
    };
    var rowArr = HEADERS.map(function (h) { return record[h]; });
    sheet.appendRow(rowArr);
    return { success: true, data: { id: record.id, model: model } };
  } catch (e) {
    return { success: false, error: String(e) };
  }
}

// ----- class aggregate (human guess vs model) -----
function getAggregate() {
  try {
    var sheet = getSheet_();
    var last = sheet.getLastRow();
    if (last < 2) {
      return { success: true, data: { n: 0, rows: [], summary: null } };
    }
    var map = headerMap_(sheet);
    var values = sheet.getRange(2, 1, last - 1, sheet.getLastColumn()).getValues();
    var rows = values
      .filter(function (r) { return r[map['status']] === 'ACTIVE'; })
      .map(function (r) {
        return {
          nickname: r[map['nickname']],
          sex: r[map['sex']],
          pclass: r[map['pclass']],
          age: r[map['age']],
          guess: r[map['guess']],
          modelVerdict: r[map['modelVerdict']],
          modelProb: r[map['modelProb']]
        };
      });
    var n = rows.length;
    var modelSurvive = 0, guessSurvive = 0, agree = 0;
    rows.forEach(function (r) {
      if (r.modelVerdict === 'survive') modelSurvive++;
      if (r.guess === 'survive') guessSurvive++;
      if (r.guess === r.modelVerdict) agree++;
    });
    return {
      success: true,
      data: {
        n: n,
        rows: rows,
        summary: {
          modelSurvive: modelSurvive,
          guessSurvive: guessSurvive,
          agree: agree,
          agreePct: n ? Math.round((agree / n) * 100) : 0
        }
      }
    };
  } catch (e) {
    return { success: false, error: String(e) };
  }
}

// ----- soft delete -----
function archiveResponse(id) {
  try {
    var sheet = getSheet_();
    var map = headerMap_(sheet);
    var last = sheet.getLastRow();
    if (last < 2) return { success: false, error: 'empty' };
    var ids = sheet.getRange(2, map['id'] + 1, last - 1, 1).getValues();
    for (var i = 0; i < ids.length; i++) {
      if (ids[i][0] === id) {
        sheet.getRange(i + 2, map['status'] + 1).setValue('ARCHIVED');
        return { success: true, data: { id: id } };
      }
    }
    return { success: false, error: 'not found' };
  } catch (e) {
    return { success: false, error: String(e) };
  }
}
