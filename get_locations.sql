SELECT TOP 1100 OwnerUserId, Location
FROM Users JOIN Posts ON Users.Id = Posts.OwnerUserId
JOIN PostTags ON Posts.Id = PostTags.PostId
JOIN Tags ON PostTags.TagId = Tags.Id
WHERE ((Tags.Id =
(SELECT Id FROM Tags WHERE Tagname = 'java'))
AND (Users.Location != ''))
GROUP BY OwnerUserId, Location
ORDER BY OwnerUserID