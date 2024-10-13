import logging
from fastapi import APIRouter, Depends, Response, status, HTTPException, BackgroundTasks
from jwt_services import current_user
from models.story import StoryOut, StoryIn, Story, StoryUpdate
from models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/v1/stories')

@router.get('/', status_code=status.HTTP_200_OK, response_model=list[StoryOut])
async def list_stories(user: User = Depends(current_user)):
    logger.info(f"User '{user.username}' is fetching all stories")
    stories = await Story.find().to_list()
    logger.info(f"Found {len(stories)} stories")
    return stories

@router.get("/{story_id}", response_model=StoryOut)
async def get_story(story_id: str, user: User = Depends(current_user)):
    logger.info(f"User '{user.username}' is fetching story with ID: {story_id}")
    story = await Story.get(story_id)
    if not story:
        logger.warning(f"Story with ID '{story_id}' not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    logger.info(f"Story with ID '{story_id}' fetched successfully")
    return story

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=StoryOut)
async def create_story(story: StoryIn, user: User = Depends(current_user)):
    logger.info(f"User '{user.username}' is creating a new story titled '{story.title}'")
    new_story = Story(
        title=story.title,
        content=story.content,
        country=story.country,
        author=user.username
    )
    await new_story.insert()
    logger.info(f"Story '{new_story.title}' created successfully with ID: {new_story.id}")
    return new_story

@router.put('/{story_id}', status_code=status.HTTP_200_OK, response_model=StoryOut)
async def update_story(
    story_id: str, 
    story_update: StoryUpdate, 
    user: User = Depends(current_user)
):
    logger.info(f"User '{user.username}' is updating story with ID: {story_id}")
    story = await Story.get(story_id)
    if not story:
        logger.warning(f"Story with ID '{story_id}' not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")

    update_data = story_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        logger.debug(f"Updating field '{field}' to '{value}'")
        setattr(story, field, value)

    await story.save()
    logger.info(f"Story with ID '{story_id}' updated successfully")
    return story

@router.delete('/{story_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_story(
    story_id: str, 
    user: User = Depends(current_user)
):
    logger.info(f"User '{user.username}' is deleting story with ID: {story_id}")
    story = await Story.get(story_id)
    
    if not story:
        logger.warning(f"Story with ID '{story_id}' not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")

    if story.author != user.username:
        logger.warning(f"User '{user.username}' is not authorized to delete story with ID: {story_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this story")

    await story.delete()
    logger.info(f"Story with ID '{story_id}' deleted successfully")


async def update_stories_country():
    logger.info("Starting batch update of stories' country field.")
    
    stories_to_update = await Story.find({"country": None}).to_list()  # Example condition
    if not stories_to_update:
        logger.info("No stories found that require updating.")
        return
    
    for story in stories_to_update:
        story.country = "Malaysia" 
        await story.save()
        logger.info(f"Updated story ID '{story.id}' with country '{story.country}'.")

    logger.info("Batch update of stories completed.")

@router.post("/update_country", status_code=status.HTTP_202_ACCEPTED)
async def trigger_country_update(background_tasks: BackgroundTasks):
    logger.info("Received request to trigger batch update of stories' country field.")
    background_tasks.add_task(update_stories_country)
    return {"message": "Batch update of stories' country field is being processed."}