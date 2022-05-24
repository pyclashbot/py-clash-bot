
function GetLatestReleaseInfo()
{
    $.getJSON("https://api.github.com/repos/matthewmiglio/py-clash-bot/releases/latest").done(function (release)
    {
        var asset = release.assets[0];
        var downloadCount = 0;
        for (var i = 0; i < release.assets.length; i++)
        {
            downloadCount += release.assets[i].download_count;
        }
        var oneHour = 60 * 60 * 1000;
        var oneDay = 24 * oneHour;
        var dateDiff = new Date() - new Date(asset.updated_at);
        var timeAgo = dateDiff < oneDay ? `${(dateDiff / oneHour).toFixed()} hours ago` : `${(dateDiff / oneDay).toFixed()} days ago`;
        var releaseInfo = `py-clash-bot ${release.name} was released ${timeAgo}.`;
        $(".download").attr("href", asset.browser_download_url);
        $(".release-info").text(releaseInfo);
        $(".release-info").fadeIn("slow");
    });
}
GetLatestReleaseInfo();
