from database.dals import UserDAL


async def test_get_users(user_dal: UserDAL):
    """Change me."""
    user_id = 1
    fetched_user = await user_dal.get_user_by_id(user_id)
    assert fetched_user
