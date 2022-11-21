from Amadeus import amadeus

urls=[
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG39707.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG35984.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG59558.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG50132.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG17947.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG69997.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG70058.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG45006.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG69796.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG70077.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG37417.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG68834.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG59215.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG42158.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG35024.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG04133.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG34479.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG47625.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG58264.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG07203.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG69893.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG56035.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG68464.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG53719.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG51111.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG63942.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG54327.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG46674.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG40158.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG45234.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG46130.html',
]

for url in urls:
    ins=amadeus.CircleInfo(url)
    ins.download_all('downloads')