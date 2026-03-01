$.ajaxSetup ({
    // Disable caching of AJAX responses
    cache: false
});

// Get a cookie value!
function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1);
        if (c.indexOf(name) == 0) return c.substring(name.length,c.length);
    }
    return "";
}

function setCookie(cname, cvalue, exdays) {    
    if (exdays != 0)
    {
        var d = new Date();
        d.setTime(d.getTime() + (exdays*24*60*60*1000));
        var expires = "expires="+d.toUTCString();
    }
    else
    {
        expires = "";
    }
    document.cookie = cname + "=" + cvalue + "; " + expires;
} 
// For anything in class "num" set to red for negative or green for positive.
function colorize()
{
    $("td.num").each(function () {
        if ($(this).is(':contains("-")'))
        { 
            $(this).addClass('red'); 
        }
        else 
        { 
            $(this).addClass('green'); 
        }
    });
}

// Hide/show stuff based on whether we're logged in.
function setPrivatePublic()
{
    if (getCookie("auth") == "")
    {
        $(".privateOnly").hide();	
        $(".publicOnly").show();
    }
    else
    {
        $(".privateOnly").show();	
        $(".publicOnly").hide();
    }
}

// Stuff to do when the document is loaded.
function readyActions()
{
    colorize();
}

function loadLinks(whenDone)
{
    if (getCookie("auth") != "")
    {
        $("#private_links").load("private_links_"+getCookie("auth")+".html", whenDone);
    }
    else
    {
        whenDone();
    }
}

function loginChange()
{
    loadLinks(setPrivatePublic);
}

// Load the title and menu bar, tweak as required.
$( "#REPLACEME" ).load("titlemenu.html", function() 
{
  // Set the heading to match the title
  document.getElementById("TITLE_TEXT").innerHTML = document.title;
  
  // The portfolio page gets no menu bar, since it takes up the entire page
  if (document.title == "Dan's share portfolio" || (document.title == "Bedlam Cube Solver" && window.innerWidth < 1000)) 
  {
    document.getElementById("LEFT").innerHTML = "";
  }

  loadLinks(setPrivatePublic);
});


// standard.js - fetches JSON data and renders charts/placeholders
(
  function(){
  function fetchData(){
    return fetch('/data.json').then(function(resp){ return resp.json(); });
  }

  function parseActivities(data){
    return (data.activities || []).map(function(a){
      return {
        date: new Date(a.date),
        distance: a.distance,
        time_seconds: a.time_seconds,
        heartrate: a.heartrate,
        elevation: a.elevation,
        notes: a.notes || '',
        tags: a.tags || []
      };
    });
  }

  function computeFitness(act){
    if (!act.time_seconds || !act.distance || !act.heartrate) return null;
    var speed = act.distance * 3600.0 / act.time_seconds;
    var heartrateAdjust = (175.0 - 80) / (act.heartrate - 80);
    var elevationAdjust = (75.0 * act.elevation) / (act.distance * 1000);
    return speed * heartrateAdjust + elevationAdjust;
  }

  function computeIntensity(act){
    if (!act.distance || !act.heartrate) return null;
    var d = Number(act.distance);
    if (!(d > 0)) return null;
    var hr = Number(act.heartrate);
    var factor = Math.pow(1.06, Math.log2(d));
    var intensity = factor * (hr - 80) * (100.0 / 122.0);
    return intensity;
  }

  function renderFitness(div, activities){
    if (!window.google || !window.google.visualization){
      // load google charts then retry
      var s = document.createElement('script');
      s.src = 'https://www.gstatic.com/charts/loader.js';
      s.onload = function(){ google.charts.load('current', {packages:['corechart']}); google.charts.setOnLoadCallback(function(){ renderFitness(div, activities); }); };
      document.head.appendChild(s);
      return;
    }

    var rows = [['Date','Fitness',{role:'style'}]];
    activities.forEach(function(a){
      var f = computeFitness(a);
      if (f !== null){
        var color = 'point {fill-color: #0000ff}';
        if ((a.tags||[]).indexOf('RACE') !== -1) color = 'point {fill-color: #ff0000}';
        if ((a.tags||[]).indexOf('TREADMILL') !== -1) color = 'point {fill-color: #32cd32}';
        rows.push([a.date, {v: f, f: a.date.toDateString()}, color]);
      }
    });

    var dataTable = google.visualization.arrayToDataTable(rows);
    var options = { title: 'Fitness', legend:{position:'none'}, explorer: { actions: ['dragToZoom','rightClickToReset'] } };
    var chartDiv = document.createElement('div'); chartDiv.style.width='800px'; chartDiv.style.height='500px'; div.appendChild(chartDiv);
    var chart = new google.visualization.ScatterChart(chartDiv);
    chart.draw(dataTable, options);
  }

  function renderIntensity(div, activities){
    if (!window.google || !window.google.visualization){
      var s = document.createElement('script');
      s.src = 'https://www.gstatic.com/charts/loader.js';
      s.onload = function(){ google.charts.load('current', {packages:['corechart']}); google.charts.setOnLoadCallback(function(){ renderIntensity(div, activities); }); };
      document.head.appendChild(s);
      return;
    }

    var rows = [['Date','Intensity',{role:'style'}]];
    activities.forEach(function(a){
      var val = computeIntensity(a);
      if (val !== null){
        var color = 'point {fill-color: #0000ff}';
        if ((a.tags||[]).indexOf('RACE') !== -1) color = 'point {fill-color: #ff0000}';
        if ((a.tags||[]).indexOf('TREADMILL') !== -1) color = 'point {fill-color: #32cd32}';
        rows.push([a.date, {v: val, f: a.date.toDateString()}, color]);
      }
    });

    var dataTable = google.visualization.arrayToDataTable(rows);
    var options = { title: 'Intensity', legend:{position:'none'}, explorer: { actions: ['dragToZoom','rightClickToReset'] } };
    var chartDiv = document.createElement('div'); chartDiv.style.width='800px'; chartDiv.style.height='500px'; div.appendChild(chartDiv);
    var chart = new google.visualization.ScatterChart(chartDiv);
    chart.draw(dataTable, options);
  }

  function renderWeekly(div, activities){
    // Limit to the last 4 years
    var cutoff = new Date();
    cutoff.setFullYear(cutoff.getFullYear() - 4);
    var weeks = {};
    activities.forEach(function(a){
      var d = new Date(a.date);
      if (d < cutoff) return; // skip older than 4 years
      // week starting on Sunday, normalize to midnight to avoid duplicate keys
      var wkStart = new Date(d);
      wkStart.setDate(d.getDate() - d.getDay());
      wkStart.setHours(0,0,0,0);
      var key = wkStart.toISOString().slice(0,10); // YYYY-MM-DD
      weeks[key] = weeks[key] || {start:new Date(wkStart.getTime()), kms:0, hasRace:false};
      weeks[key].kms += Number(a.distance || 0);
      if ((a.tags||[]).indexOf('RACE') !== -1) weeks[key].hasRace = true;
    });
    var rows = [['Week','Kilometres',{role:'style'}]];
    Object.keys(weeks).sort().forEach(function(k){ var w = weeks[k]; rows.push([new Date(k).toDateString(), w.kms, w.hasRace ? '#ff0000' : null]); });

    // render using Google Charts
    if (!window.google || !window.google.visualization){
      var s = document.createElement('script');
      s.src = 'https://www.gstatic.com/charts/loader.js';
      s.onload = function(){ google.charts.load('current', {packages:['corechart']}); google.charts.setOnLoadCallback(function(){ renderWeekly(div, activities); }); };
      document.head.appendChild(s);
      return;
    }
    var dataTable = google.visualization.arrayToDataTable(rows);
    var options = { title: 'Kilometres per week', legend:{position:'none'}, vAxis:{viewWindowMode:'explicit', viewWindow:{min:0}} };
    var chartDiv = document.createElement('div'); chartDiv.style.width='800px'; chartDiv.style.height='500px'; div.appendChild(chartDiv);
    var chart = new google.visualization.ColumnChart(chartDiv);
    chart.draw(dataTable, options);
  }

  function expectedRaceHeartrate(distance){
    // crude mapping from distance (km) to expected race heart rate
    if (!distance) return 175;
    if (distance <= 6) return 187;
    if (distance <= 12) return 181;
    if (distance <= 30) return 175;
    return 169;
  }

  function renderRaces(div, data){
    var activities = parseActivities(data);
    var races = activities.filter(function(a){ return (a.raceName && a.raceName.length>0) || ((a.tags||[]).indexOf('RACE') !== -1); });
    if (races.length === 0){ div.textContent = 'No races found in data'; return; }

    // For each race compute prior-12-week training kms and a performance measure (fitness-like)
    var rows = [[
      'Training kms',
      'Performance',
      {type:'string', role:'tooltip'},
      {role:'style'}
    ]];
    races.forEach(function(r){
      var rd = new Date(r.date);
      var windowStart = new Date(rd);
      windowStart.setDate(rd.getDate() - 84); // 12 weeks
      var prior = activities.filter(function(a){ var d=new Date(a.date); return d >= windowStart && d < rd; });
      var trainingKms = prior.reduce(function(sum,a){ return sum + (Number(a.distance)||0); }, 0);

      // compute a performance metric: use heartrate if present, else expected based on race distance
      var hr = Number(r.heartrate) || expectedRaceHeartrate(Number(r.distance));
      var perf = null;
      if (r.time_seconds && r.distance){
        var speed = r.distance * 3600.0 / r.time_seconds;
        var heartrateAdjust = (175.0 - 80) / (hr - 80 || 1);
        var elevationAdjust = (75.0 * (Number(r.elevation)||0)) / (Number(r.distance) * 1000 || 1);
        perf = speed * heartrateAdjust + elevationAdjust;
      } else {
        // fallback: use distance as proxy (so the point still appears)
        perf = Number(r.distance) || 0;
      }

      var tooltip = (r.raceName||'Race') + '\n' + new Date(r.date).toDateString() + '\nTraining: ' + Math.round(trainingKms) + ' km' + (r.time_seconds ? '\nTime: ' + Math.floor(r.time_seconds/60)+':' + (('0'+(r.time_seconds%60)).slice(-2)) : '');
      var dist = Number(r.distance) || 0;
      // Colour-code by distance: marathon (red), half (orange), 10k (gold), 5k (green)
      var color = '#3366cc';
      if (dist >= 42) color = '#ff0000';
      else if (dist >= 21.1) color = '#ff8000';
      else if (dist >= 10) color = '#ffd700';
      else if (dist >= 5) color = '#32cd32';
      // Ensure numeric typing for the first two columns
      trainingKms = Number(trainingKms) || 0;
      perf = Number(perf) || 0;
      rows.push([trainingKms, perf, String(tooltip), color]);
    });

    if (!window.google || !window.google.visualization){
      var s = document.createElement('script');
      s.src = 'https://www.gstatic.com/charts/loader.js';
      s.onload = function(){ google.charts.load('current', {packages:['corechart']}); google.charts.setOnLoadCallback(function(){ renderRaces(div, data); }); };
      document.head.appendChild(s);
      return;
    }

    var dataTable = google.visualization.arrayToDataTable(rows);
    var options = { title: 'Race performance vs training (12 weeks)', legend:{position:'none'}, explorer:{actions:['dragToZoom','rightClickToReset']}, hAxis:{title:'Training kms (prev 12 weeks)'}, vAxis:{title:'Performance'} };
    var chartDiv = document.createElement('div'); chartDiv.style.width='800px'; chartDiv.style.height='500px'; div.appendChild(chartDiv);
    var chart = new google.visualization.ScatterChart(chartDiv);
    chart.draw(dataTable, options);
  }

  function renderRecords(div, data){
    var activities = parseActivities(data);
    var totalDistance = 0;
    var totalTime = 0;
    var numRuns = activities.length;
    activities.forEach(function(a){ totalDistance += Number(a.distance||0); totalTime += Number(a.time_seconds||0); });
    if (data && data.summary && data.summary.total_distance){ totalDistance = Number(data.summary.total_distance); }

    function formatHMS(sec){ sec = Math.round(sec); var h = Math.floor(sec/3600); var m = Math.floor((sec%3600)/60); var s = sec%60; return h+':'+('0'+m).slice(-2)+':'+('0'+s).slice(-2); }
    function formatMS(sec){ sec = Math.round(sec); var m = Math.floor(sec/60); var s = sec%60; return m+':'+('0'+s).slice(-2); }

    var out = '';
    out += '<p>Since March 2012:</p>';

    // Totals
    out += '<p>Total:</p><ul>';
    out += '<li>Distance run:       ' + Math.round(totalDistance) + 'km</li>';
    out += '<li>Number of runs:     ' + numRuns + '</li>';
    out += '<li>Time spent running: ' + Math.floor(totalTime/3600) + ' hours</li>';
    out += '</ul>';

    // Per year
    out += '<p>Distance per year:</p><ul>';
    var nowYear = new Date().getFullYear();
    for (var year = 2012; year <= nowYear; year++){
      var yearStart = new Date(year,0,1);
      var yearEnd = new Date(year,11,31,23,59,59);
      var yearKm = activities.filter(function(a){ var d=new Date(a.date); return d >= yearStart && d <= yearEnd; }).reduce(function(s,a){ return s + Number(a.distance||0); }, 0);
      out += '<li>' + year + ':                 ' + Math.round(yearKm) + 'km</li>';
    }
    out += '</ul>';

    // Averages
    out += '<p>Average:</p><ul>';
    var avgRunLen = numRuns? (totalDistance / numRuns) : 0;
    var avgRunTime = numRuns? (totalTime / numRuns) : 0;
    out += '<li>Run length: ' + avgRunLen.toFixed(1) + 'km</li>';
    out += '<li>Run time:   ' + formatHMS(avgRunTime) + '</li>';
    var secondsPerKm = totalDistance? (totalTime / totalDistance) : 0;
    out += '<li>Pace:       ' + Math.floor(secondsPerKm/60) + ':' + ('0'+Math.round(secondsPerKm%60)).slice(-2) + ' per km</li>';
    // Average heart rate (time-weighted)
    var hrSum = 0; var hrTime = 0;
    activities.forEach(function(a){ if (a.heartrate && a.time_seconds){ hrSum += Number(a.heartrate) * Number(a.time_seconds); hrTime += Number(a.time_seconds); } });
    var avgHR = hrTime? Math.round(hrSum / hrTime) : 'N/A';
    out += '<li>Heart rate: ' + (avgHR==='N/A'? avgHR : (avgHR + ' bpm')) + '</li>';
    out += '</ul>';

    // Bests
    out += '<p>Personal bests:</p><ul>';
    // Longest run (time)
    var longestTime = 0; activities.forEach(function(a){ if (a.time_seconds && a.time_seconds > longestTime) longestTime = a.time_seconds; });
    out += '<li>Longest run:        ' + formatHMS(longestTime) + '</li>';
    // Furthest
    var furthest = 0; activities.forEach(function(a){ if (a.distance && a.distance > furthest) furthest = a.distance; });
    out += '<li>Furthest run:       ' + Math.round(furthest) + 'km</li>';
    // Highest average HR
    var highestHR = 0; activities.forEach(function(a){ if (a.heartrate && a.heartrate > highestHR) highestHR = a.heartrate; });
    out += '<li>Highest average HR: ' + (highestHR||'N/A') + '</li>';

    // Longest running streak
    var dateKeys = Object.keys(activities.reduce(function(acc,a){ var k=(new Date(a.date)).toISOString().slice(0,10); acc[k]=true; return acc; }, {})).sort();
    var longest = 0; var firstdate = null; var lastdate = null; var streak = 0; var prev = null; var curFirst = null; var curLast = null;
    dateKeys.forEach(function(k){ var d = new Date(k); if (!prev){ streak=1; curFirst=d; curLast=d; } else { var diff = Math.round((d - prev)/(1000*60*60*24)); if (diff===1){ streak++; curLast=d; } else { streak=1; curFirst=d; curLast=d; } } if (streak>longest){ longest=streak; firstdate=new Date(curFirst); lastdate=new Date(curLast); } prev=d; });
    out += '<li>Longest running streak: ' + (longest||0) + ' days ' + (firstdate?('('+firstdate.toDateString()+' to '+lastdate.toDateString()+')') : '') + '</li>';

    // Best times for distances
    function bestFor(minDist){ var best=null; activities.forEach(function(a){ if (a.distance && a.distance >= minDist && a.time_seconds){ if (!best || a.time_seconds < best.time_seconds) best = a; } }); return best; }
    var b5 = bestFor(5.0); var b10 = bestFor(10.0); var b21 = bestFor(21.1); var b42 = bestFor(42.2);
    out += '<li>5km:                ' + (b5? (formatMS(b5.time_seconds) + ' (' + (b5.raceName||new Date(b5.date).toDateString()) + ')') : 'N/A') + '</li>';
    out += '<li>10km:               ' + (b10? (formatMS(b10.time_seconds) + ' (' + (b10.raceName||new Date(b10.date).toDateString()) + ')') : 'N/A') + '</li>';
    out += '<li>21km:               ' + (b21? (formatHMS(b21.time_seconds) + ' (' + (b21.raceName||new Date(b21.date).toDateString()) + ')') : 'N/A') + '</li>';
    out += '<li>42km:               ' + (b42? (formatHMS(b42.time_seconds) + ' (' + (b42.raceName||new Date(b42.date).toDateString()) + ')') : 'N/A') + '</li>';
    out += '</ul>';

    div.innerHTML = out;
  }

  function renderShoes(div, activities){
    var shoes = {};
    activities.forEach(function(a){ if (a.shoes){ shoes[a.shoes] = (shoes[a.shoes]||0) + a.distance; } });
    var ul = document.createElement('ul');
    Object.keys(shoes).forEach(function(s){ var li = document.createElement('li'); li.textContent = s+': '+Math.round(shoes[s])+' km'; ul.appendChild(li); });
    div.appendChild(ul);
  }

  function renderTreadmill(div, data){
    var activities = parseActivities(data).filter(function(a){ return (a.tags||[]).indexOf('TREADMILL') !== -1; });
    var purchaseDate = new Date(2014,10,21); // 2014-11-21 (month is 0-based)
    var runs = activities.filter(function(a){ return new Date(a.date) >= purchaseDate; });
    var cost = 1600;
    var daysOwned = Math.floor((new Date() - purchaseDate) / (1000*60*60*24));
    var timesUsed = runs.length;
    var distance = runs.reduce(function(s,a){ return s + (Number(a.distance)||0); }, 0);
    var costPerKm = distance? (cost / distance) : 0;
    var costPerRun = timesUsed? (cost / timesUsed) : 0;

    var out = '<ul>';
    out += '<li>Owned for:      ' + daysOwned + ' days</li>';
    out += '<li>Times used:     ' + timesUsed + '</li>';
    out += '<li>Distance run:   ' + Math.round(distance) + 'km</li>';
    out += '<li>Cost per km:    &pound;' + costPerKm.toFixed(2) + '</li>';
    out += '<li>Cost per run:   &pound;' + costPerRun.toFixed(2) + '</li>';
    out += '</ul>';
    div.innerHTML = out;
  }

  function renderGym(div, data){
    var activities = parseActivities(data).filter(function(a){ return (a.tags||[]).indexOf('TREADMILL') !== -1; });
    var startDate = new Date(2012,8,1); // 2012-09-01
    var endDate = new Date(2013,11,1);  // 2013-12-01
    var runs = activities.filter(function(a){ var d = new Date(a.date); return d >= startDate && d <= endDate; });
    var cost = 200;
    var timesUsed = runs.length;
    var distance = runs.reduce(function(s,a){ return s + (Number(a.distance)||0); }, 0);
    var costPerKm = distance? (cost / distance) : 0;
    var costPerRun = timesUsed? (cost / timesUsed) : 0;

    var out = '<ul>';
    out += '<li>Member for:     1 year</li>';
    out += '<li>Times used:     ' + timesUsed + '</li>';
    out += '<li>Distance run:   ' + Math.round(distance) + 'km</li>';
    out += '<li>Cost per km:    &pound;' + costPerKm.toFixed(2) + '</li>';
    out += '<li>Cost per run:   &pound;' + costPerRun.toFixed(2) + '</li>';
    out += '</ul>';
    div.innerHTML = out;
  }

  function renderStreak(div, data){
    var activities = parseActivities(data).sort(function(a,b){ return new Date(a.date) - new Date(b.date); });
    if (!activities || activities.length===0){ div.textContent = 'No activity data'; return; }

    // Build a sorted list of unique run dates
    var dateSet = {};
    activities.forEach(function(a){ var k = (new Date(a.date)).toISOString().slice(0,10); dateSet[k]=true; });
    var dates = Object.keys(dateSet).map(function(k){ return new Date(k); }).sort(function(a,b){ return a - b; });

    // Find longest consecutive-day streak (similar to Period.longestStreak)
    var longest = 0; var firstdate = null; var lastdate = null;
    var streak = 0; var current_firstdate = null; var current_lastdate = null; var prev = null;
    dates.forEach(function(d){
      if (!prev){ streak = 1; current_firstdate = d; current_lastdate = d; }
      else {
        var diff = Math.round((d - prev) / (1000*60*60*24));
        if (diff === 1){
          streak += 1;
          current_lastdate = d;
        } else if (diff > 1){
          streak = 1;
          current_firstdate = d;
          current_lastdate = d;
        }
      }
      if (streak > longest){ longest = streak; firstdate = new Date(current_firstdate); lastdate = new Date(current_lastdate); }
      prev = d;
    });

    if (!firstdate){ div.textContent = 'No streaks found'; return; }

    // Gather activities in the longest-streak range (inclusive)
    var startKey = firstdate.toISOString().slice(0,10);
    var endKey = lastdate.toISOString().slice(0,10);
    var streakActivities = activities.filter(function(a){ var k = (new Date(a.date)).toISOString().slice(0,10); return k >= startKey && k <= endKey; });

    // Compute stats
    var totalDistance = streakActivities.reduce(function(s,a){ return s + (Number(a.distance)||0); }, 0);
    var numRuns = streakActivities.length;
    var totalTime = streakActivities.reduce(function(s,a){ return s + (Number(a.time_seconds)||0); }, 0);
    var avgRunLength = numRuns? (totalDistance / numRuns) : 0;
    var avgRunTimeSec = numRuns? (totalTime / numRuns) : 0;
    function formatHMS(sec){ sec = Math.round(sec); var h = Math.floor(sec/3600); var m = Math.floor((sec%3600)/60); var s = sec%60; return h+':'+('0'+m).slice(-2)+':'+('0'+s).slice(-2); }
    var secondsPerKm = totalDistance? (totalTime / totalDistance) : 0;

    // Average heart rate weighted by time (if available)
    var hbSum = 0; var timeMeasured = 0;
    streakActivities.forEach(function(a){ if (a.heartrate && a.heartrate>0 && a.time_seconds){ hbSum += Number(a.heartrate) * Number(a.time_seconds); timeMeasured += Number(a.time_seconds); } });
    var avgHR = timeMeasured? Math.round(hbSum / timeMeasured) : null;

    // Render HTML matching original webExporter.writeStreak
    var out = '';
    out += '<p>' + longest + ' days from ' + firstdate.toDateString() + ' to ' + lastdate.toDateString() + ':</p>';
    out += '<ul style="list-style-type:none;padding-left:0;">';
    out += '<li>Distance run:       ' + Math.round(totalDistance) + 'km</li>';
    out += '<li>Number of runs:     ' + numRuns + '</li>';
    out += '<li>Time spent running: ' + Math.floor(totalTime/3600) + ' hours</li>';
    out += '<li>Average run length: ' + (avgRunLength? avgRunLength.toFixed(1) : '0.0') + 'km</li>';
    out += '<li>Average run time:   ' + formatHMS(avgRunTimeSec) + '</li>';
    out += '<li>Average pace:       ' + Math.floor(secondsPerKm/60) + ':' + ('0'+Math.round(secondsPerKm%60)).slice(-2) + ' per km</li>';
    out += '<li>Average heart rate: ' + (avgHR? (avgHR + 'bpm') : 'N/A') + '</li>';
    out += '</ul>';

    div.innerHTML = out;
  }

  function renderTag(div, tag, data){
    var activities = parseActivities(data);
    switch(tag){
      case 'FITNESS': renderFitness(div, activities); break;
      case 'INTENSITY': renderIntensity(div, activities); break;
      case 'TRAINING': renderFitness(div, activities); break;
      case 'WEEKLY': renderWeekly(div, activities); break;
      case 'RECORDS': renderRecords(div, data); break;
      case 'RECENT': renderRecords(div, data); break;
      case 'SHOES': renderShoes(div, activities); break;
      case 'STREAK': renderStreak(div, data); break;
      case 'RACES': renderRaces(div, data); break;
      case 'TREADMILL': renderTreadmill(div, data); break;
      case 'GYM': renderGym(div, data); break;
      default: div.textContent = 'No renderer for '+tag;
    }
  }

  // Initialize: find all divs with data-tag and render after fetching data
  document.addEventListener('DOMContentLoaded', function(){
    var targets = document.querySelectorAll('div[data-tag]');
    if (!targets || targets.length===0) return;
    fetchData().then(function(data){
      targets.forEach(function(t){ renderTag(t, t.getAttribute('data-tag'), data); });
    }).catch(function(err){ console.error('Failed to load data.json', err); targets.forEach(function(t){ t.textContent = 'Failed to load data'; }); });
  });

})();

// When we're ready, do the stuff we need to do when we're ready.
$(document).ready( readyActions );

