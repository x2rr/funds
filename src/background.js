
import axios from 'axios';


var Interval;
var isDuringDate = () => {
	var curDate = new Date();
	var beginDateAM = new Date();
	var endDateAM = new Date();
	var beginDatePM = new Date();
	var endDatePM = new Date();

	beginDateAM.setHours(9, 30, 0);
	endDateAM.setHours(11, 30, 0);
	beginDatePM.setHours(13, 0, 0);
	endDatePM.setHours(15, 0, 0);
	if (curDate.getDay() == '6' || curDate.getDay() == '0') {
		return false;
	} else if (curDate >= beginDateAM && curDate <= endDateAM) {
		return true;
	} else if (curDate >= beginDatePM && curDate <= endDatePM) {
		return true;
	} else {
		return false;
	}
}

var setBadge = fundcode => {

	let url =
		"http://fundgz.1234567.com.cn/js/" +
		fundcode +
		".js?rt=" +
		new Date().getTime();
	axios
		.get(url)
		.then(res => {
			let val = res.data.match(/\{(.+?)\}/);
			let ress = JSON.parse(val[0]);
			chrome.browserAction.setBadgeText({
				text: ress.gszzl
			});
			let color = ress.gszzl > 0 ? '#ff0000' : '#008000'
			chrome.browserAction.setBadgeBackgroundColor({
				color: color
			});
		})
		.catch(error => {
			chrome.browserAction.setBadgeText({
				text: ''
			});
		});

	if (!isDuringDate()) {
		chrome.browserAction.setBadgeBackgroundColor({
			color: [0, 0, 0, 0]
		});
	}

}

var startInterval = RealtimeFundcode => {
	endInterval(Interval);
	setBadge(RealtimeFundcode);
	Interval = setInterval(() => {
		if (isDuringDate()) {
			setBadge(RealtimeFundcode);
		} else {
			chrome.browserAction.setBadgeBackgroundColor({
				color: [0, 0, 0, 0]
			});
		}
	}, 3 * 60 * 1000)

}

var endInterval = () => {
	clearInterval(Interval);
	chrome.browserAction.setBadgeText({
		text: ''
	});
}

var RealtimeFundcode = null;

chrome.storage.sync.get('RealtimeFundcode', (res) => {
	RealtimeFundcode = res.RealtimeFundcode ? res.RealtimeFundcode : null;
	if (RealtimeFundcode) {
		startInterval(RealtimeFundcode);
	} else {
		endInterval();
	}
});


chrome.runtime.onMessage.addListener(
	function (request, sender, sendResponse) {
		if (request.type == "DuringDate") {
			let DuringDate = isDuringDate();
			sendResponse({
				farewell: DuringDate
			});
		}
		if (request.type == "endInterval") {
			endInterval()
		}
		if (request.type == "startInterval") {
			startInterval(request.id)
		}

	});