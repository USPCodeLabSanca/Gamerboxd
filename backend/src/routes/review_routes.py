from fastapi import Depends, status, Request
from fastapi.responses import JSONResponse
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from models.schemas import *
from services.security_services import *
from services.db_services import *
from utils.dependencies import get_conn, require_login

review_router = InferringRouter(prefix="/review", tags=["review"])

@cbv(review_router)
class NewReviewController:
    @review_router.post("/")
    async def create_review(self, review: ReviewIn, conn = Depends(get_conn), user_id = Depends(require_login)):
        try:
            review_for_insertion = await is_review_insertion_valid(conn, review, user_id)

        except HTTPException as he:
            raise he
        
        except Exception as e:
            raise HTTPException(500, detail=str(e))
        
        review_creation_result = await DB_create_review(conn, review_for_insertion, user_id)

        if not review_creation_result.success or not review_creation_result.obj:
            raise HTTPException(500, str(review_creation_result.error))
        
        return JSONResponse({"message":review_creation_result.message}, status.HTTP_202_ACCEPTED)
                            
@cbv(review_router)       
class UpdateReviewController:
    @review_router.put("/{old_review_game}")
    async def update_review(self, old_review_game: int, new_review: ReviewIn, conn = Depends(get_conn), user_id = Depends(require_login)):  
        try:
            review_for_update = await is_review_update_valid(conn, new_review, old_review_game, user_id)

        except HTTPException as he:
            raise he
        
        except Exception as e:
            raise HTTPException(500, detail=str(e))

        review_update_result = await DB_update_review(conn, review_for_update, old_review_game, user_id)

        if not review_update_result.success or not review_update_result.obj:
            raise HTTPException(500, str(review_update_result.error))
        
        return JSONResponse((review_update_result.obj).model_dump(), status.HTTP_202_ACCEPTED)

                                                       
@cbv(review_router)
class DeleteReviewController:
    @review_router.delete("/{review_game}")
    async def delete_review(self, review_game: int, conn = Depends(get_conn), user_id = Depends(require_login)):
        review_delete_result = await DB_delete_review(conn, review_game, user_id)

        if not review_delete_result.success:
            raise HTTPException(500, str(review_delete_result.error))
        
        return JSONResponse({"message":review_delete_result.message}, status.HTTP_202_ACCEPTED)
    
@cbv(review_router)
class LikeReviewController:
    @review_router.post("/like/{username}/{game}")
    async def like_review(self, username: str, game: int, conn = Depends(get_conn), user_id = Depends(require_login)):

        review_id_result = await DB_read_review_id(conn, username, game)
        if not review_id_result.success or not review_id_result.obj:
            raise HTTPException(500, str(review_id_result.error))

        review_id = review_id_result.obj

        try:
            like_for_insertion = await is_liked(conn, review_id, user_id)

            if like_for_insertion is not None:
                raise HTTPException(400, detail="Você já deu like nessa review!")
            
        except HTTPException as he:
            raise he
        
        except Exception as e:
            raise HTTPException(500, detail=str(e))

        review_like_result = await DB_create_like_review(conn, ReviewLike(user_a = user_id, review = review_id))

        if not review_like_result.success:
            raise HTTPException(500, str(review_like_result.error))

        return JSONResponse({"message": review_like_result.message}, status.HTTP_202_ACCEPTED)
    
@cbv(review_router)
class UnlikeReviewController:
    @review_router.post("/unlike/{username}/{game}")
    async def unlike_review(self, username: str, game: int, conn = Depends(get_conn), user_id = Depends(require_login)):

        review_id_result = await DB_read_review_id(conn, username, game)

        if not review_id_result.success or not review_id_result.obj:
            raise HTTPException(500, str(review_unlike_result.error))

        review_id = review_id_result.obj

        try:
            like_for_removal = await is_liked(conn, review_id, user_id)

            if like_for_removal is None:
                raise HTTPException(400, detail="Você não deu like nessa review!")
            
        except HTTPException as he:
            raise he
        
        except Exception as e:
            raise HTTPException(500, detail=str(e))


        review_unlike_result = await DB_delete_like_review(conn, ReviewLike(user_a = user_id, review = review_id))
        
        if not review_unlike_result.success:
            raise HTTPException(500, str(review_unlike_result.error))

        return JSONResponse({"message": review_unlike_result.message}, status.HTTP_202_ACCEPTED)
    
@cbv(review_router)
class GetAllReviewsController:
    @review_router.get("/{username}")
    async def get_all_reviews(self, username: str, limit: int = 10, conn = Depends(get_conn)):
        if limit > 20:
            raise HTTPException(400, "Não podem ser apresentadas mais de 20 reviews!")
        
        reviews_result = await DB_read_limit_reviews(conn, username, limit)

        if not reviews_result.success or not reviews_result.obj:
            raise HTTPException(500, str(reviews_result.error))

        return JSONResponse(content=[review.model_dump() for review in reviews_result.obj],status_code = status.HTTP_200_OK)
        

@cbv(review_router)
class GetOneReviewController:
    @review_router.get("/{username}/{game}")
    async def get_one_review(self, username: str, game: int, conn = Depends(get_conn)):
        review_result = await DB_read_review(conn, username, game)

        if not review_result.success: 
            raise HTTPException(500, str(review_result.error))
        
        return JSONResponse(review_result.obj.model_dump(), status.HTTP_200_OK)